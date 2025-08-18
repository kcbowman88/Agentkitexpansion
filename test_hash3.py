import hashlib

keys = ("test_thread", "KB_QA", "D", "proof_data", "2")
seed = "|".join(keys)
print(f"seed: {seed}")
h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
print(f"hash: {h}")
idx = int(h[:16], 16) % 4
print(f"index: {idx}")
print(int(h[:16], 16) % 4)