from pathlib import Path
from unittest.mock import patch
import pytest
import requests
from processing.guard_cli import is_supported_language, check_api_available, save_pdf
from processing.tests.test_utils import create_mock_response

# Constants
API_ENDPOINT = "http://localhost:5000"
SUPPORTED_LANGUAGES = ["en", "it", "de"]
UNSUPPORTED_LANGUAGES = ["xx", "a"] # Anything other than supported
TEST_PDF_FILENAME = "example.pdf"
OUTPUT_DIR = Path("/some/output/dir")
REDACTED_PREFIX = "REDACTED_"


class TestLanguageSupport:
    """Tests for language support functionality."""

    @pytest.mark.unit
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_supported_languages(self, language):
        """Test that supported languages return True."""
        assert is_supported_language(language) is True

    @pytest.mark.unit
    @pytest.mark.parametrize("language", UNSUPPORTED_LANGUAGES)
    def test_unsupported_languages(self, language):
        """Test that unsupported languages return False."""
        assert is_supported_language(language) is False


class TestPDFOperations:
    """Tests for PDF-related operations."""

    @pytest.mark.unit
    def test_save_pdf_success(self, mocker):
        """Test that PDFs are saved with the correct path and prefix."""
        mock_pdf = mocker.Mock()
        mock_pdf.name = TEST_PDF_FILENAME
        mock_save = mocker.patch.object(mock_pdf, "save")
        
        save_pdf(mock_pdf, OUTPUT_DIR)
        
        expected_output_path = OUTPUT_DIR / f"{REDACTED_PREFIX}{TEST_PDF_FILENAME}"
        mock_save.assert_called_once_with(str(expected_output_path))


class TestAPIConnectivity:
    """Tests for API connectivity checks."""

    @pytest.mark.unit
    def test_check_api_available_success(self):
        """Test API check succeeds when server returns 200."""
        with patch("processing.guard_cli.requests.get") as mock_get:
            mock_get.return_value = create_mock_response(200)
            # Shouldn't raise SystemExit
            check_api_available(API_ENDPOINT)

    @pytest.mark.unit
    def test_check_api_available_http_error(self):
        """Test API check fails with SystemExit when server returns error status."""
        with patch("processing.guard_cli.requests.get") as mock_get:
            mock_get.return_value = create_mock_response(500)
            with pytest.raises(SystemExit):
                check_api_available(API_ENDPOINT)

    @pytest.mark.unit
    def test_check_api_available_connection_error(self):
        """Test API check fails with SystemExit when connection fails."""
        with patch("processing.guard_cli.requests.get",
                  side_effect=requests.exceptions.ConnectionError("Connection failed")):
            with pytest.raises(SystemExit):
                check_api_available(API_ENDPOINT)