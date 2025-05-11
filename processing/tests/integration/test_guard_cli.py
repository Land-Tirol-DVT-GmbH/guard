import pytest
import fitz
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from processing.guard_cli import save_pdf, process_pdf, process_document_list

# Utils
def create_mock_response(status_code=200, json_data=None):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data
    return mock_response

# Fixtures
@pytest.fixture
def sample_pdf():
    """Create a real temporary PDF file for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        temp_dir = Path(tmp_dir_name)
        pdf_path = temp_dir / "sample.pdf"
        
        doc = fitz.open()
        page = doc.new_page()
        
        text = """Dies ist ein Beispieltext mit PII.
        Franz Müller wohnt in der Musterstraße 12, 1010 Wien.
        Seine Telefonnummer ist +43 660 1234567."""
        
        page.insert_text((50, 50), text)
        doc.save(str(pdf_path))
        doc.close()
        
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
def test_integration_process_pdf(sample_pdf, mock_presidio_response):
    """Integration test for processing a real PDF file. Mocking only Presidio API call."""
    pdf_path, temp_dir = sample_pdf
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = create_mock_response(200, mock_presidio_response)
        
        pdf = fitz.open(str(pdf_path))
        process_pdf(pdf)
        save_pdf(pdf, output_dir)
        
        expected_output = output_dir / f"REDACTED_{pdf_path.name}"
        assert expected_output.exists()
        
        assert mock_post.call_count == len(pdf)
        
        pdf.close()

@pytest.mark.integration
def test_integration_process_document_list(sample_pdf, mock_presidio_response):
    """Integration test for processing a list of real PDF documents. Mocking only Presidio API call."""
    
    pdf_path, temp_dir = sample_pdf
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    # pdf names for checking if log folder exists
    pdf_name_1 = "sample"
    pdf_name_2 = "sample_2"

    # Second PDF for testing list processing
    second_pdf_path = temp_dir / pdf_name_2
    doc2 = fitz.open()
    page = doc2.new_page()
    page.insert_text((50, 50), "This is another sample PDF to test whether a list of PDFs can also be processed by this function.")
    doc2.save(str(second_pdf_path))
    doc2.close()
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = create_mock_response(200, mock_presidio_response)
        
        try:
            pdf1 = fitz.open(str(pdf_path))
            pdf2 = fitz.open(str(second_pdf_path))
            
            document_list = [pdf1, pdf2]
            process_document_list(document_list=document_list, output_dir=output_dir, log_to_json=True)
            
            expected_output1 = output_dir / f"REDACTED_{pdf_path.name}"
            expected_output2 = output_dir / f"REDACTED_{second_pdf_path.name}"
            expected_log_output1 = output_dir / f"{pdf_name_1}_LOGS" / "page_0.json"
            expected_log_output2 = output_dir / f"{pdf_name_2}_LOGS" / "page_0.json"
            assert expected_output1.exists()
            assert expected_output2.exists()
            assert expected_log_output1.exists()
            assert expected_log_output2.exists()

        finally:
            if 'pdf1' in locals():
                pdf1.close()
            if 'pdf2' in locals():
                pdf2.close()


@pytest.mark.integration
def test_integration_process_document_list_presidio_returns_500(sample_pdf, capsys):
    """Integration test for processing a real PDF with a 500 response by presidion. Mocking only Presidio API call."""
    pdf_path, temp_dir = sample_pdf
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = create_mock_response(500, None)
        
        pdf = fitz.open(str(pdf_path))
        pdf_name = Path(pdf.name).name

        document_list = [pdf]
        process_document_list(document_list, output_dir, False)

        captured = capsys.readouterr()

        assert "Presidio error for:" in captured.out
        assert f"{pdf_name}" in captured.out
        
        expected_output = output_dir /f"REDACTED_{pdf_path.name}"
        assert expected_output.exists()

        pdf.close()