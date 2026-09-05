import unittest
import sys
import os

# Add scripts to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from pre_gen import is_valid_pattern, get_pattern

class TestPreGen(unittest.TestCase):
    def test_pattern_extraction(self):
        # Example TRON address: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
        address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        # First 4 after T: R7NH
        # Last 5: jLj6t
        self.assertEqual(get_pattern(address), "R7NH*jLj6t")

    def test_exclusion_logic(self):
        # Contains '0' in first 4
        self.assertFalse(is_valid_pattern("T0ABC...12345"))
        # Contains 'O' in last 5
        self.assertFalse(is_valid_pattern("TABC1...123O5"))
        # Valid address
        self.assertTrue(is_valid_pattern("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"))

if __name__ == "__main__":
    unittest.main()
