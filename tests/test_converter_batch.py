import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from rdt.core.converter import CoreIngestor, ConversionError

class TestCoreIngestorBatch(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path("test_output")
        self.ingestor = CoreIngestor(self.output_dir)

    def tearDown(self):
        if self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)

    @patch("rdt.core.converter.CoreIngestor.process_file")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.rglob")
    def test_process_batch_directory(self, mock_rglob, mock_is_dir, mock_process_file):
        mock_is_dir.return_value = True
        mock_rglob.side_effect = [
            [Path("test1.pdf"), Path("test2.pdf")], # for .pdf
            [Path("test3.docx")] # for .docx
        ]
        
        callback = MagicMock()
        result = self.ingestor.process_batch([Path("some_dir")], on_progress=callback)
        
        self.assertEqual(result.total, 3)
        self.assertEqual(len(result.successes), 3)
        self.assertEqual(callback.call_count, 6) # 2 calls per file (start/end)

    @patch("rdt.core.converter.CoreIngestor.process_file")
    def test_process_batch_with_failures(self, mock_process_file):
        mock_process_file.side_effect = [None, Exception("Failed")]
        
        paths = [Path("success.pdf"), Path("fail.pdf")]
        # Mock existence
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.is_dir", return_value=False):
                result = self.ingestor.process_batch(paths)
        
        self.assertEqual(len(result.successes), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.failures[0][1], "Failed")

    def test_unsupported_file_type(self):
        with patch("pathlib.Path.exists", return_value=True):
            with self.assertRaises(ConversionError):
                self.ingestor.process_file(Path("test.txt"))

    @patch("shutil.which")
    def test_convert_pdf_missing_engines(self, mock_which):
        mock_which.return_value = None
        # Mock fitz as None
        with patch("rdt.core.converter.fitz", None):
            with self.assertRaises(ConversionError) as cm:
                self.ingestor._convert_pdf(Path("test.pdf"), Path("out.md"))
            self.assertIn("No suitable engine found", str(cm.exception))

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_convert_docx_failure(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=1, stderr=b"error")
        
        with self.assertRaises(ConversionError):
            self.ingestor._convert_docx(Path("test.docx"), Path("out.md"))
