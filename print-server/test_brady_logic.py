import os
import unittest
from services import BradyLabelService
from database import DatabaseService

class TestBradyLogic(unittest.TestCase):
    def setUp(self):
        self.output_folder = "temp_test_labels"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.label_service = BradyLabelService(output_folder=self.output_folder)
        self.db_service = DatabaseService(db_path=":memory:") # Use in-memory for tests

    def test_batch_generation(self):
        """Verify that batch generation creates a PDF and correctly increments serials"""
        system = "TestSystem"
        year = "2024"
        month = "01"
        start_serial = "0001"
        quantity = 5
        
        pdf_path = self.label_service.generate_batch(system, year, month, start_serial, quantity)
        self.assertTrue(os.path.exists(pdf_path))
        print(f"Generated PDF at: {pdf_path}")

    def test_duplicate_prevention(self):
        """Verify that database correctly tracks and prevents duplicate serials"""
        system = "SystemA"
        year = "2024"
        month = "05"
        
        # 1. First print: 0001 to 0005
        self.db_service.record_prints(system, year, month, "0001", 5)
        
        # 2. Check duplicates in a range that overlaps
        # Range: 0004 to 0008 (Overlap: 0004, 0005)
        duplicates = self.db_service.check_duplicates(system, year, month, "0004", 5)
        self.assertEqual(len(duplicates), 2)
        self.assertIn("0004", duplicates)
        self.assertIn("0005", duplicates)
        
        # 3. Check range with no overlaps
        duplicates = self.db_service.check_duplicates(system, year, month, "0006", 5)
        self.assertEqual(len(duplicates), 0)

    def test_leading_zeros(self):
        """Ensure leading zeros are preserved in database checks"""
        system = "SystemB"
        year = "2024"
        month = "06"
        
        self.db_service.record_prints(system, year, month, "0010", 2) # prints 0010, 0011
        
        duplicates = self.db_service.check_duplicates(system, year, month, "0010", 1)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0], "0010")

if __name__ == '__main__':
    unittest.main()
