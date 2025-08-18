import hashlib
from collections import defaultdict

# Simulate the occurrence counter from the objection handler
_occurrence_counter = defaultdict(int)

def _increment_occurrence(thread_id: str, node_id: str, objection_cat: str) -> int:
    key = (thread_id, node_id, objection_cat)
    _occurrence_counter[key] += 1
    return _occurrence_counter[key]

def deterministic_index(keys: tuple, mod: int) -> int:
    """
    Deterministic index using stable SHA256 over pipe-joined keys; returns 0 if mod<=0.
    Logs chosen index for traceability.
    """
    try:
        if mod <= 0:
            return 0
        seed = "|".join(keys)
        print(f"seed: {seed}")
        h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        print(f"hash: {h}")
        idx = int(h, 16) % mod
        print(f"index: {idx}")
        return idx
    except Exception:
        return 0

# Test the occurrence counter and deterministic index together
thread = "test_thread"
node_for_banks = "KB_QA"
persona = "D"
objection_cat_norm = "too_good_to_be_true"

print("=== First objection ===")
occ1 = _increment_occurrence(thread, node_for_banks, objection_cat_norm)
print(f"occurrence: {occ1}")
keys1 = (thread, node_for_banks, persona, objection_cat_norm, str(occ1))
idx1 = deterministic_index(keys1, 4)

print("\n=== Second objection ===")
occ2 = _increment_occurrence(thread, node_for_banks, objection_cat_norm)
print(f"occurrence: {occ2}")
keys2 = (thread, node_for_banks, persona, objection_cat_norm, str(occ2))
idx2 = deterministic_index(keys2, 4)

print("\n=== Third objection ===")
occ3 = _increment_occurrence(thread, node_for_banks, objection_cat_norm)
print(f"occurrence: {occ3}")
keys3 = (thread, node_for_banks, persona, objection_cat_norm, str(occ3))
idx3 = deterministic_index(keys3, 4)

print(f"\nResults: occurrence=1 -> index={idx1}, occurrence=2 -> index={idx2}, occurrence=3 -> index={idx3}")