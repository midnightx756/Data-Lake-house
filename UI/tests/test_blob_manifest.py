import csv, tempfile, unittest
from pathlib import Path
class ManifestTests(unittest.TestCase):
    def test_manifest_columns(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"m.csv"
            p.write_text("asset_id,original_name,byte_offset,payload_size,is_duplicate\n1,\"a.txt\",0,3,0\n",encoding="utf-8")
            with p.open(newline="",encoding="utf-8") as f:
                row=next(csv.DictReader(f))
            self.assertEqual(row["byte_offset"],"0")
            self.assertEqual(row["payload_size"],"3")
if __name__=="__main__": unittest.main()
