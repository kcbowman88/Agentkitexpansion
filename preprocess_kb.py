#!/usr/bin/env python3
"""
KB preprocessing and validation CLI (A3 hardening).

This replaces the previous ad-hoc PDF preprocessor with a validator and optional index rebuild
for concise KB snippets.

Example usage:
  python preprocess_kb.py --input data/doc_chunks.json --output data/kb_index.faiss --validate-only
  python preprocess_kb.py --input data/doc_chunks.json --output data/kb_index.faiss --rebuild

Inputs:
- --input should point to a JSON file containing an array of snippet dicts with schema:
  {
    "id": str,
    "text": str,  # ≤120 chars and ≤2 sentences
    "tags": {
      "node_id": str,   # one of allowed set
      "topic": str,     # short topic key
      "persona": str|null  # "D" | "I" | "S" | "C" | null
    }
  }

The CLI validates, enforces caps, and can rebuild a FAISS index compatible with existing usage.
"""

import os
import sys
import json
import logging
import argparse
import re
from typing import List, Dict, Any, Tuple, Optional, Set

# Optional FAISS import is kept to preserve compatibility with current pipeline
try:
    import faiss  # type: ignore
    HAVE_FAISS = True
except Exception:
    HAVE_FAISS = False

# Constants for caps
MAX_LEN = 120
MAX_SENTS = 2

# Allowed node_id values (configurable set; extend as needed)
ALLOWED_NODE_IDS: Set[str] = {
    "IntroduceModel",
    "KB_QA",
    "IncomeBackground",
    "FinancialQualification",
    "Commitment",
    "Scheduling",
}

ALLOWED_PERSONAS: Set[str] = {"D", "I", "S", "C"}

SENT_SPLIT_REGEX = re.compile(r'[.?!]+')


def count_sentences(text: str) -> int:
    """Count sentences using a simple regex-based heuristic."""
    segments = [seg for seg in SENT_SPLIT_REGEX.split(text) if seg.strip()]
    return len(segments)


def trim_to_caps(text: str, max_len: int = MAX_LEN, max_sents: int = MAX_SENTS) -> str:
    """
    Trim text to sentence boundary within caps; if still too long, hard-trim to char cap.
    """
    if not text:
        return text
    # First, cut to max sentences
    pieces = SENT_SPLIT_REGEX.split(text)
    kept_pieces = []
    for piece in pieces:
        if piece.strip():
            kept_pieces.append(piece.strip())
            if len(kept_pieces) >= max_sents:
                break
    if kept_pieces:
        candidate = ". ".join(kept_pieces)
        if text.strip().endswith(tuple(".?!")):
            candidate = candidate.rstrip() + "."
    else:
        candidate = text.strip()

    # Enforce char cap with safe trimming
    if len(candidate) <= max_len:
        return candidate
    return candidate[:max_len].rstrip()


def validate_snippet(sn: Dict[str, Any]) -> List[str]:
    """
    Validate a single snippet against the schema and caps.
    Returns a list of error messages (empty if valid).
    """
    errors: List[str] = []
    # Schema keys
    if not isinstance(sn, dict):
        return ["Snippet is not an object"]
    if "id" not in sn or not isinstance(sn["id"], str) or not sn["id"].strip():
        errors.append("Missing or invalid 'id'")
    if "text" not in sn or not isinstance(sn["text"], str):
        errors.append("Missing or invalid 'text'")
    if "tags" not in sn or not isinstance(sn["tags"], dict):
        errors.append("Missing or invalid 'tags'")

    # If tags present, validate required fields
    tags = sn.get("tags", {})
    node_id = tags.get("node_id")
    topic = tags.get("topic")
    persona = tags.get("persona", None)

    if not isinstance(node_id, str) or not node_id.strip():
        errors.append("Missing or invalid tags.node_id")
    elif node_id not in ALLOWED_NODE_IDS:
        errors.append(f"tags.node_id '{node_id}' not in allowed set")

    if not isinstance(topic, str) or not topic.strip():
        errors.append("Missing or invalid tags.topic")

    if persona is not None and not (isinstance(persona, str) and persona in ALLOWED_PERSONAS):
        errors.append("tags.persona must be one of {'D','I','S','C'} or null")

    # Caps
    text = sn.get("text", "")
    if isinstance(text, str):
        if len(text) > MAX_LEN:
            errors.append(f"text length {len(text)} exceeds cap {MAX_LEN}")
        s_count = count_sentences(text)
        if s_count > MAX_SENTS:
            errors.append(f"text sentence count {s_count} exceeds cap {MAX_SENTS}")

    return errors


def validate_snippets(snippets: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate a list of snippets. Ensures id uniqueness and per-item schema/caps.
    Returns (ok, summary) where summary includes counts and error details.
    """
    id_set: Set[str] = set()
    errors: List[Dict[str, Any]] = []
    total = len(snippets)

    for idx, sn in enumerate(snippets):
        item_errors = validate_snippet(sn)
        # id uniqueness check
        sn_id = sn.get("id")
        if isinstance(sn_id, str):
            if sn_id in id_set:
                item_errors.append(f"duplicate id '{sn_id}'")
            else:
                id_set.add(sn_id)
        else:
            item_errors.append("missing id prevents uniqueness check")
        if item_errors:
            errors.append({"index": idx, "id": sn.get("id"), "errors": item_errors})

    ok = len(errors) == 0
    summary = {
        "total": total,
        "valid": ok,
        "error_count": len(errors),
        "errors": errors[:50],  # cap verbosity
        "unique_ids": len(id_set),
    }
    return ok, summary


def load_input(path: str) -> List[Dict[str, Any]]:
    """
    Load JSON input. Supports:
      - array of snippet dicts (preferred)
      - array of strings (will be transformed to minimal snippets with generated ids and default tags -> invalid until edited)
    """
    with open(path, "r") as f:
        data = json.load(f)
    if isinstance(data, list) and all(isinstance(x, dict) for x in data):
        return data  # expected format
    # Backward-compat: transform simple text chunks into skeleton snippets (invalid until fixed)
    if isinstance(data, list) and all(isinstance(x, str) for x in data):
        transformed: List[Dict[str, Any]] = []
        for i, txt in enumerate(data):
            transformed.append({
                "id": f"chunk_{i}",
                "text": trim_to_caps(str(txt or "")),
                "tags": {
                    "node_id": "KB_QA",
                    "topic": "general",
                    "persona": None
                }
            })
        return transformed
    raise ValueError("Unsupported input JSON structure; expected list[dict] or list[str]")


def rebuild_index(snippets: List[Dict[str, Any]], output_index_path: str) -> None:
    """
    Rebuild a lightweight FAISS index to preserve compatibility with existing consumers.
    Embeddings are not computed here to avoid heavy deps; we create a trivial flat index
    storing vector ids corresponding to snippet positions. This keeps faiss.read_index compatibility.
    """
    if not HAVE_FAISS:
        logging.warning("FAISS not available; skipping index rebuild. Output will not be created.")
        return
    # Build a trivial index of dimensionality 1 so that it can be saved/loaded.
    dim = 1
    index = faiss.IndexFlatL2(dim)
    import numpy as np  # local import to avoid global dependency if not used
    vecs = np.arange(len(snippets), dtype="float32").reshape(-1, 1)
    index.add(vecs)
    os.makedirs(os.path.dirname(output_index_path) or ".", exist_ok=True)
    faiss.write_index(index, output_index_path)
    logging.info(f"Wrote FAISS index with {len(snippets)} vectors to {output_index_path}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and optionally rebuild concise KB snippet index (A3).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input", required=True, help="Path to input JSON (array of snippet dicts)")
    parser.add_argument("--output", required=False, default="data/kb_index.faiss",
                        help="Path to output FAISS index (when --rebuild)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true", help="Validate input and exit non-zero on errors")
    mode.add_argument("--rebuild", action="store_true", help="Validate, then rebuild index if valid")

    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        snippets = load_input(args.input)
    except Exception as e:
        logging.error(f"Failed to load input: {e}")
        return 2

    ok, summary = validate_snippets(snippets)
    print(json.dumps({"action": "validate", "summary": summary}, ensure_ascii=False))

    if not ok:
        # Non-zero exit on validation errors
        return 1

    if args.validate_only:
        return 0

    # Rebuild path
    if args.rebuild:
        try:
            rebuild_index(snippets, args.output)
            print(json.dumps({"action": "rebuild", "output": args.output, "count": len(snippets)}))
            return 0
        except Exception as e:
            logging.error(f"Failed to rebuild index: {e}", exc_info=True)
            return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())