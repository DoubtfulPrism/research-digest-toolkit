import unittest
from unittest.mock import patch
from rdt.core.validator import DependencyValidator

class TestDependencyValidator(unittest.TestCase):
    def setUp(self):
        self.validator = DependencyValidator()

    @patch("shutil.which")
    def test_check_all_success(self, mock_which):
        # Mock all tools found
        mock_which.side_effect = lambda x: f"/usr/bin/{x}"
        
        results = self.validator.check_all()
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.found for r in results))
        self.assertEqual(results[0].name, "pdftotext")
        self.assertEqual(results[0].path, "/usr/bin/pdftotext")

    @patch("shutil.which")
    def test_check_all_partial_failure(self, mock_which):
        # Mock pdftotext not found, pandoc found
        mock_which.side_effect = lambda x: "/usr/bin/pandoc" if x == "pandoc" else None
        
        results = self.validator.check_all()
        
        pdftotext = next(r for r in results if r.name == "pdftotext")
        pandoc = next(r for r in results if r.name == "pandoc")
        
        self.assertFalse(pdftotext.found)
        self.assertEqual(pdftotext.path, "NOT FOUND")
        self.assertTrue(pandoc.found)
        self.assertEqual(pandoc.path, "/usr/bin/pandoc")

    @patch("shutil.which")
    def test_is_conversion_possible(self, mock_which):
        # All found -> True
        mock_which.return_value = "/usr/bin/tool"
        self.assertTrue(self.validator.is_conversion_possible())
        
        # One missing -> False
        mock_which.side_effect = lambda x: "/usr/bin/tool" if x == "pandoc" else None
        self.assertFalse(self.validator.is_conversion_possible())
