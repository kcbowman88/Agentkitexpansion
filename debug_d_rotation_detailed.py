import hashlib

# Let's debug the deterministic_index function from the objection handler
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
        idx = int(h[:16], 16) % mod
        print(f"index: {idx}")
        print(f"First 16 chars of hash as int: {int(h[:16], 16)}")
        return idx
    except Exception:
        return 0

# Test with the exact keys that would be used for KB_QA with D persona
# For occurrence=1
keys1 = ("test_thread", "KB_QA", "D", "too_good_to_be_true", "1")
print("=== occurrence=1 ===")
idx1 = deterministic_index(keys1, 4)

# For occurrence=2
keys2 = ("test_thread", "KB_QA", "D", "too_good_to_be_true", "2")
print("\n=== occurrence=2 ===")
idx2 = deterministic_index(keys2, 4)

# For occurrence=3
keys3 = ("test_thread", "KB_QA", "D", "too_good_to_be_true", "3")
print("\n=== occurrence=3 ===")
idx3 = deterministic_index(keys3, 4)

print(f"\nResults: occurrence=1 -> index={idx1}, occurrence=2 -> index={idx2}, occurrence=3 -> index={idx3}")