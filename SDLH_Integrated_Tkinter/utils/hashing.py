import hashlib
from config import HASH_CHUNK_SIZE
def sha256_file(path, chunk_size=HASH_CHUNK_SIZE):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk: break
            digest.update(chunk)
    return digest.hexdigest()
