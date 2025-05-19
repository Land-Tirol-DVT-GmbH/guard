import pytest
import fitz
import tempfile
from pathlib import Path
from unittest.mock import patch
from processing.guard_cli import save_pdf, save_logs_for_pdf, process_pdf, process_document_list
from processing.tests.test_utils import create_test_pdf, create_mock_response

# Constants
SAMPLE_PDF_NAME = "sample"
SAMPLE_PDF_2_NAME = "sample_2"
REDACTED_PREFIX = "REDACTED_"
HIGHLIGHTED_PREFIX = "HIGHLIGHTED_"
LOGS_SUFFIX = "_LOGS"

# Test Data
SAMPLE_TEXT = """Dies ist ein Beispieltext mit PII.
Franz Müller wohnt in der Musterstraße 12, 1010 Wien.
Seine Telefonnummer ist +43 660 1234567."""

SAMPLE_TEXT_2 = "This is another sample PDF to test whether a list of PDFs can also be processed by this function."

# Fixtures
@pytest.fixture
def output_dir():
    """Create a temporary output directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        temp_dir = Path(tmp_dir_name)
        output = temp_dir / "output"
        output.mkdir(exist_ok=True)
        yield temp_dir, output

@pytest.fixture
def sample_pdf(output_dir):
    """Create a real temporary PDF file for testing."""
    temp_dir, _ = output_dir
    pdf_path = temp_dir / f"{SAMPLE_PDF_NAME}.pdf"
    create_test_pdf(pdf_path, SAMPLE_TEXT)
    yield pdf_path, temp_dir

@pytest.fixture
def mock_presidio_response():
    """Create a realistic Presidio API response."""
    return [
        {
            "start": 33,
            "end": 43,
            "score": 0.95,
            "entity_type": "PERSON"
        },
        {
            "start": 58,
            "end": 88,
            "score": 0.85,
            "entity_type": "ADDRESS"
        },
        {
            "start": 100,
            "end": 118,
            "score": 0.9,
            "entity_type": "PHONE_NUMBER"
        }
    ]

# Tests
@pytest.mark.integration
def test_integration_process_pdf_redact(sample_pdf, output_dir, mock_presidio_response):
    """Integration test for processing a PDF file with redaction."""
    pdf_path, _ = sample_pdf
    _, output_dir = output_dir
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = create_mock_response(200, mock_presidio_response)
        
        with fitz.open(str(pdf_path)) as pdf:
            process_pdf(pdf)
            save_pdf(pdf, output_dir)
            
            expected_output = output_dir / f"{REDACTED_PREFIX}{pdf_path.name}"
            assert expected_output.exists()
            assert mock_post.call_count == len(pdf)

@pytest.mark.integration
def test_integration_process_pdf_highlight(sample_pdf, output_dir, mock_presidio_response):
    """Integration test for processing a PDF file with highlighting and logging."""
    pdf_path, _ = sample_pdf
    _, output_dir = output_dir
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = create_mock_response(200, mock_presidio_response)
        
        with fitz.open(str(pdf_path)) as pdf:
            log_dict = process_pdf(pdf, generate_log=True, should_redact=False)
            save_pdf(pdf, output_dir, has_been_highlighted=True)
            save_logs_for_pdf(pdf=pdf, output_dir=output_dir, log_dict=log_dict)
            
            expected_output = output_dir / f"{HIGHLIGHTED_PREFIX}{SAMPLE_PDF_NAME}.pdf"
            expected_log_output = output_dir / f"{SAMPLE_PDF_NAME}{LOGS_SUFFIX}" / "page_0.json"
            
            assert expected_output.exists()
            assert expected_log_output.exists()
            assert mock_post.call_count == len(pdf)

@pytest.mark.integration
def test_integration_process_document_list(sample_pdf, output_dir, mock_presidio_response):
    """Integration test for processing a list of PDF documents."""
    pdf_path, temp_dir = sample_pdf
    _, output_dir = output_dir
    
    # Create second PDF for testing list processing
    second_pdf_path = temp_dir / f"{SAMPLE_PDF_2_NAME}.pdf"
    create_test_pdf(second_pdf_path, SAMPLE_TEXT_2)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = create_mock_response(200, mock_presidio_response)
        
        with fitz.open(str(pdf_path)) as pdf1, fitz.open(str(second_pdf_path)) as pdf2:
            document_list = [pdf1, pdf2]
            process_document_list(document_list=document_list, output_dir=output_dir, log_to_json=True)
            
            expected_output1 = output_dir / f"{REDACTED_PREFIX}{pdf_path.name}"
            expected_output2 = output_dir / f"{REDACTED_PREFIX}{second_pdf_path.name}"
            expected_log_output1 = output_dir / f"{SAMPLE_PDF_NAME}{LOGS_SUFFIX}" / "page_0.json"
            expected_log_output2 = output_dir / f"{SAMPLE_PDF_2_NAME}{LOGS_SUFFIX}" / "page_0.json"
            
            assert expected_output1.exists()
            assert expected_output2.exists()
            assert expected_log_output1.exists()
            assert expected_log_output2.exists()

@pytest.mark.integration
def test_integration_process_document_list_presidio_returns_500(sample_pdf, output_dir, capsys):
    """Integration test for handling Presidio API errors (HTTP 500)."""
    pdf_path, _ = sample_pdf
    _, output_dir = output_dir
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = create_mock_response(500, None)
        
        with fitz.open(str(pdf_path)) as pdf:
            pdf_name = Path(pdf.name).name
            document_list = [pdf]
            process_document_list(document_list, output_dir, False)
            
            captured = capsys.readouterr()
            expected_output = output_dir / f"{REDACTED_PREFIX}{pdf_path.name}"
            
            assert "Presidio error for:" in captured.out
            assert f"{pdf_name}" in captured.out
            assert expected_output.exists()