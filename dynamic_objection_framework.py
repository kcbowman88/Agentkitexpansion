import warnings
warnings.warn("This module is deprecated and will be removed in a future version. Please use 'generative_objection_handler' instead.", DeprecationWarning)

import hashlib
import logging
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple, Any

import yaml

from objection_handler import ObjectionContext  # reuse existing context type
from caller_agent import finalize_agent_text, _sanitize_opener_response  # last-mile guards


@dataclass
class Profile:
    ack_tokens: list
    pivot_tokens: list
    require_ack_first: bool = True
    require_pivot: bool = True
    max_sentences: int = 4
    human_like_denylist: list = None
    allow_explicit_resume: bool = True


@dataclass
class Templates:
    value_cues: list
    micro_asks: list
    pivots: list


class ProfileStore:
    def __init__(self):
        self._profiles: Dict[Tuple[str, str], Profile] = {}

    def load_from_yaml(self, node_id: str, persona: str, path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        prof = Profile(
            ack_tokens=data.get("ack_tokens", []),
            pivot_tokens=data.get("bridge_rules", {}).get("pivot_tokens", []),
            require_ack_first=data.get("bridge_rules", {}).get("require_ack_first", True),
            require_pivot=data.get("bridge_rules", {}).get("require_pivot", True),
            max_sentences=data.get("bridge_rules", {}).get("max_sentences", 4),
            human_like_denylist=data.get("human_like", {}).get("denylist", []),
            allow_explicit_resume=data.get("human_like", {}).get("allow_explicit_resume", True),
        )
        self._profiles[(node_id, persona.upper())] = prof

    def for_node(self, node_id: str, persona: str) -> Profile:
        key = (node_id, (persona or "S").upper())
        # fallback to opener family if specific not present
        return self._profiles.get(key) or self._profiles.get(("*", key[1])) or self._profiles.get(("*", "*"))


class TemplateStore:
    def __init__(self):
        self._templates: Dict[Tuple[str, str], Templates] = {}

    def load_from_yaml(self, node_id: str, persona: str, path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        tpl = Templates(
            value_cues=data.get("value_cues", []),
            micro_asks=data.get("micro_asks", []),
            pivots=data.get("pivots", []),
        )
        self._templates[(node_id, persona.upper())] = tpl

    def for_node(self, node_id: str, persona: str) -> Templates:
        key = (node_id, (persona or "S").upper())
        return self._templates.get(key) or self._templates.get(("*", key[1])) or self._templates.get(("*", "*"))


FactoryFn = Callable[[Profile, Templates], Callable[[ObjectionContext, str], str]]


class DynamicHandlerRegistry:
    def __init__(self, profiles: ProfileStore, templates: TemplateStore):
        self.profiles = profiles
        self.templates = templates
        # key: (node_id|*, persona|*, category|*) -> factory
        self.factories: Dict[Tuple[str, str, str], FactoryFn] = {}

    def register(self, node_id: str, persona: str, category: str, factory: FactoryFn):
        self.factories[(node_id or "*", (persona or "*").upper(), category or "*")] = factory

    def resolve(self, node_id: str, persona: str, category: str) -> Optional[FactoryFn]:
        p = (node_id or "*", (persona or "S").upper(), category or "*")
        return (
            self.factories.get(p)
            or self.factories.get(("*", p[1], p[2]))
            or self.factories.get(("*", "*", p[2]))
            or self.factories.get(("*", "*", "*"))
        )

    def build_handler(self, node_id: str, persona: str, category: str) -> Optional[Callable[[ObjectionContext, str], str]]:
        factory = self.resolve(node_id, persona, category)
        if not factory:
            return None
        prof = self.profiles.for_node(node_id, persona)
        tpls = self.templates.for_node(node_id, persona)
        return factory(prof, tpls)


# -------- Utility selection with deterministic rotation --------

def _pick(options: list, seed_tuple: Tuple[str, ...]) -> Optional[str]:
    options = [o for o in (options or []) if isinstance(o, str) and o.strip()]
    if not options:
        return None
    h = hashlib.sha256("|".join(seed_tuple).encode("utf-8")).hexdigest()
    idx = int(h, 16) % len(options)
    return options[idx]


def _sentence_join(parts: list) -> str:
    cleaned = [p.strip().rstrip(".") for p in parts if p and isinstance(p, str)]
    if not cleaned:
        return ""
    return ". ".join(cleaned) + "."


def _apply_human_like_denylist(text: str, denylist: list) -> str:
    if not text:
        return text
    low = text.lower()
    for bad in (denylist or []):
        if bad and bad.lower() in low:
            # strip phrase by replacing with benign space
            low = low.replace(bad.lower(), "")
    # naive reconstruct with original casing lost — safe since finalizers/sanitizers will reshape
    # return original text when no match; else return low with capitalization best-effort
    if low == text.lower():
        return text
    # Capitalize first letter
    out = low.strip()
    return out[0:1].upper() + out[1:] if out else text


# -------- Factory implementations (Opener S minimal slice) --------

def opener_s_factory(profile: Profile, templates: Templates) -> Callable[[ObjectionContext, str], str]:
    """
    Build a handler enforcing:
      - ack-first (from profile.ack_tokens)
      - value cue (rotate)
      - micro-ask (rotate)
      - pivot enforcement (pivot last; ensure a pivot token present)
      - pass through finalize_agent_text and opener sanitizer
    """
    def handler(ctx: ObjectionContext, user_text: str) -> str:
        seed_base = (
            ctx.thread_id or "thread",
            ctx.node_id or "node",
            (ctx.persona or "S").upper(),
            "opener_s_v1",
            user_text or "",
        )
        parts = []

        # ack-first
        ack = _pick(profile.ack_tokens, seed_base + ("ack",))
        if profile.require_ack_first and ack:
            parts.append(ack)

        # value cue
        val = _pick(templates.value_cues, seed_base + ("val",))
        if val:
            parts.append(val)

        # micro-ask
        ask = _pick(templates.micro_asks, seed_base + ("ask",))
        if ask:
            parts.append(ask)

        # pivot — ensure present and last if required
        pivot = _pick(templates.pivots, seed_base + ("pivot",))
        if profile.require_pivot and pivot:
            parts.append(pivot)

        text = _sentence_join(parts)

        # human-like denylist scrub
        text = _apply_human_like_denylist(text, profile.human_like_denylist)

        # finalize + sanitizer (last-mile)
        try:
            shaped = finalize_agent_text(ctx, text, is_objection=True)  # ctx is ObjectionContext but finalize reads attributes; ObjectionContext has minimal fields
        except Exception:
            # if finalize_agent_text expects state-like object, map minimal attributes
            shaped = text
        try:
            if (ctx.node_id or "") in ("N_Opener_StackingIncomeHook_V3_CreativeTactic", "N_IntroduceModel_And_AskQuestions_V3_Adaptive", "N_IntroduceModel_And_AskQuestions_V3_Adaptive_Steady"):
                shaped = _sanitize_opener_response(shaped, persona=(ctx.persona or "S"))
        except Exception:
            pass

        return shaped
    return handler


def build_minimal_registry(opener_profile_path: str, opener_templates_path: str) -> DynamicHandlerRegistry:
    """
    Create a registry and load opener S profiles/templates from YAML.
    Registers factories for categories: general_disinterest, early_dismissal, no_recall, objection_or_callback_request.
    """
    profiles = ProfileStore()
    templates = TemplateStore()

    # Load for opener node family, persona S
    node_ids = [
        "N_Opener_StackingIncomeHook_V3_CreativeTactic",
        "N_IntroduceModel_And_AskQuestions_V3_Adaptive",
        "N_IntroduceModel_And_AskQuestions_V3_Adaptive_Steady",
    ]
    for nid in node_ids:
        profiles.load_from_yaml(nid, "S", opener_profile_path)
        templates.load_from_yaml(nid, "S", opener_templates_path)

    reg = DynamicHandlerRegistry(profiles, templates)

    # Register factories per category for opener S
    for nid in node_ids:
        for cat in ("general_disinterest", "early_dismissal", "no_recall", "objection_or_callback_request"):
            reg.register(nid, "S", cat, opener_s_factory)

    # Global wildcard (fallback)
    reg.register("*", "S", "*", opener_s_factory)

    return reg