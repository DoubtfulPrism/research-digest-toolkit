import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rdt.core.converter import CoreIngestor, ConversionError

@pytest.fixture
def sample_pdf(tmp_path):
    # Create a dummy PDF file (just an empty file for basic path checking)
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy content")
    return pdf_file

@pytest.fixture
def sample_docx(tmp_path):
    docx_file = tmp_path / "sample.docx"
    docx_file.write_bytes(b"dummy docx content")
    return docx_file

@patch("rdt.core.converter.shutil.which")
@patch("rdt.core.converter.subprocess.Popen")
@patch("rdt.core.converter.subprocess.run")
def test_native_linux_engine_pdf(mock_subprocess_run, mock_subprocess_popen, mock_which, tmp_path, sample_pdf):
    # Simulate pdftotext and pandoc are installed
    mock_which.side_effect = lambda x: f"/usr/bin/{x}"
    
    # Simulate successful subprocess runs
    mock_p1 = MagicMock()
    mock_p1.returncode = 0
    mock_subprocess_popen.return_value = mock_p1
    
    mock_run_result = MagicMock()
    mock_run_result.returncode = 0
    mock_subprocess_run.return_value = mock_run_result
    
    ingestor = CoreIngestor(output_dir=tmp_path)
    output_file = ingestor.process_file(sample_pdf)
    
    assert output_file.exists()
    assert output_file.suffix == ".md"
    assert "sample.md" == output_file.name
    
    # Should have called subprocess for pdftotext | pandoc pipeline
    assert mock_subprocess_run.called

@patch("rdt.core.converter.shutil.which")
def test_fallback_pymupdf_engine_pdf(mock_which, tmp_path, sample_pdf):
    # Simulate missing native tools
    mock_which.return_value = None
    
    ingestor = CoreIngestor(output_dir=tmp_path)
    
    # We expect PyMuPDF to be used.
    # We should mock fitz (PyMuPDF) fully
    mock_fitz = MagicMock()
    with patch("rdt.core.converter.fitz", mock_fitz):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Extracted text"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.open.return_value.__enter__.return_value = mock_doc
        
        output_file = ingestor.process_file(sample_pdf)
        
        assert output_file.exists()
        assert output_file.suffix == ".md"
        assert output_file.read_text() == "Extracted text"

def test_missing_tools_and_no_fallback(tmp_path, sample_docx):
    # If the file is DOCX, PyMuPDF can't handle it, and if pandoc is missing, it should raise an error
    with patch("rdt.core.converter.shutil.which", return_value=None):
        ingestor = CoreIngestor(output_dir=tmp_path)
        with pytest.raises(ConversionError, match="No suitable engine"):
            ingestor.process_file(sample_docx)
