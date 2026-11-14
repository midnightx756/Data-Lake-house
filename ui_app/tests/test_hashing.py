import tempfile, unittest
from pathlib import Path
from utils.hashing import sha256_file
class HashingTests(unittest.TestCase):
    def test_known_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.txt"; p.write_bytes(b"abc")
            self.assertEqual(sha256_file(p),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
if __name__=="__main__": unittest.main()
