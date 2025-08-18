import hashlib

keys = ('global', 'IntroduceModel', 'D', 'too_good_to_be_true', '3')
seed = "|".join(keys)
print(f"seed: {seed}")
h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
print(f"hash: {h}")
idx = int(h[:16], 16) % 4
print(f"index: {idx}")
print(f"First 16 chars of hash as int: {int(h[:16], 16)}")