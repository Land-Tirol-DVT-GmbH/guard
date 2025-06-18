import pytest
import json
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """Create a test client for the Flask app with a mocked analyzer engine."""
    from app import create_app

    with patch('app.create_analyzer_engine') as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_engine.analyze.return_value = [
            MagicMock(
                entity_type="PERSON",
                start=0,
                end=9,
                score=0.85,
                to_dict=lambda: {
                    "entity_type": "PERSON",
                    "start": 0,
                    "end": 9,
                    "score": 0.85
                }
            )
        ]

        person_recognizer = MagicMock(name="PersonRecognizer")
        person_recognizer.name = "PersonRecognizer"
        
        email_recognizer = MagicMock(name="EmailRecognizer")
        email_recognizer.name = "EmailRecognizer"
        
        license_recognizer = MagicMock(name="AUTLicensePlateRecognizer")
        license_recognizer.name = "AUTLicensePlateRecognizer"
        
        mock_engine.get_recognizers.return_value = [
            person_recognizer,
            email_recognizer,
            license_recognizer
        ]
        
        mock_engine.get_supported_entities.return_value = [
            "PERSON", "EMAIL_ADDRESS", "AUT_LICENSE_PLATE", "LOCATION", "PHONE_NUMBER"
        ]

        app = create_app()
        app.config['TESTING'] = True

        with app.test_client() as client:
            yield client, mock_engine

class TestAnalyzerApp:
    """Integration tests for the analyzer app endpoints."""
    
    def test_health_endpoint(self, client):
        """Test that health endpoint returns a 200 response."""
        test_client, _ = client
        response = test_client.get('/health')
        
        assert response.status_code == 200
        assert response.data.decode('utf-8') == "Presidio Analyzer service is up"
    
    def test_analyze_endpoint_success(self, client):
        """Test that analyze endpoint returns correct results with valid input."""
        test_client, mock_engine = client

        test_input = {
            "text": "John Smith lives in Vienna.",
            "language": "en"
        }

        response = test_client.post(
            '/analyze',
            data=json.dumps(test_input),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert mock_engine.analyze.called

        response_data = json.loads(response.data)
        assert isinstance(response_data, list)
        assert len(response_data) > 0
        assert response_data[0]['entity_type'] == 'PERSON'
        assert response_data[0]['score'] == 0.85
    
    def test_analyze_endpoint_missing_text(self, client):
        """Test that analyze endpoint handles missing text correctly."""
        test_client, _ = client

        test_input = {
            "language": "en"
        }

        response = test_client.post(
            '/analyze',
            data=json.dumps(test_input),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert "No text provided" in response_data["error"]
    
    def test_analyze_endpoint_missing_language(self, client):
        """Test that analyze endpoint handles missing language correctly."""
        test_client, _ = client

        test_input = {
            "text": "John Smith lives in Vienna."
        }

        response = test_client.post(
            '/analyze',
            data=json.dumps(test_input),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert "No language provided" in response_data["error"]
    
    def test_recognizers_endpoint(self, client):
        """Test that recognizers endpoint returns correct list of recognizers."""
        test_client, mock_engine = client

        response = test_client.get('/recognizers?language=en')

        assert response.status_code == 200
        assert mock_engine.get_recognizers.called

        response_data = json.loads(response.data)
        assert isinstance(response_data, list)
        assert "PersonRecognizer" in response_data
        assert "EmailRecognizer" in response_data
        assert "AUTLicensePlateRecognizer" in response_data
    
    def test_supported_entities_endpoint(self, client):
        """Test that supported_entities endpoint returns correct list of entities."""
        test_client, mock_engine = client

        response = test_client.get('/supportedentities?language=en')

        assert response.status_code == 200
        assert mock_engine.get_supported_entities.called

        response_data = json.loads(response.data)
        assert isinstance(response_data, list)
        assert "PERSON" in response_data
        assert "EMAIL_ADDRESS" in response_data
        assert "AUT_LICENSE_PLATE" in response_data
        assert "LOCATION" in response_data
        assert "PHONE_NUMBER" in response_data
    
    def test_error_handling(self, client):
        """Test error handling for failed analyzer engine calls."""
        test_client, mock_engine = client

        mock_engine.analyze.side_effect = Exception("Test error")

        test_input = {
            "text": "John Smith lives in Vienna.",
            "language": "en"
        }

        response = test_client.post(
            '/analyze',
            data=json.dumps(test_input),
            content_type='application/json'
        )

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert "An internal server error has occurred!" in response_data["error"]