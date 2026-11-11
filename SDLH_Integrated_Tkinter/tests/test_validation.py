import unittest
from security.validation import validate_sql_readonly
class ValidationTests(unittest.TestCase):
    def test_select_allowed(self): self.assertEqual(validate_sql_readonly("SELECT 1"),"SELECT 1")
    def test_delete_rejected(self):
        with self.assertRaises(ValueError): validate_sql_readonly("DELETE FROM assets")
if __name__=="__main__": unittest.main()
