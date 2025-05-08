import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from unittest.mock import patch, MagicMock

import requests

from processing.guard_cli import is_supported_language, check_api_available, save_pdf

def test_is_supported_language():
    assert is_supported_language("en") is True
    assert is_supported_language("it") is True
    assert is_supported_language("de") is True
    assert is_supported_language("xx") is False
    assert is_supported_language("a") is False

def test_save_pdf_success(mocker):
    mock_pdf = mocker.Mock()
    mock_pdf.name = "example.pdf"
    mock_save = mocker.patch.object(mock_pdf, "save")
    output_dir = Path("/some/output/dir")
    
    save_pdf(mock_pdf, output_dir)
    
    expected_output_path = output_dir / "REDACTED_example.pdf"
    mock_save.assert_called_once_with(str(expected_output_path))


#Test api availability

def test_check_api_available_success():
    with patch("processing.guard_cli.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Should not raise SystemExit
        check_api_available("http://localhost:5000")

def test_check_api_available_http_error():
    with patch("processing.guard_cli.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(SystemExit):
            check_api_available("http://localhost:5000")

def test_check_api_available_connection_error():
    with patch("processing.guard_cli.requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed")):
        with pytest.raises(SystemExit):
            check_api_available("http://localhost:5000")