LANGUAGES = ["de", "en", "it"]

def create_mock_response(status_code=200, json_data=None):
    """Create a mock HTTP response with specified status code and JSON data."""
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data
    return mock_response

def strip_scores(results):
    """Remove score field from recognition results for easier comparison."""
    return [{"type": r.entity_type, "start": r.start, "end": r.end} for r in results]

def get_expected_text(test_case):
    """Extract the expected detected text from a test case using its ranges."""
    text = test_case["text"]
    return [text[e["start"]:e["end"]] for e in test_case["expected"]]

def create_test_pdf(path, text):
    """Create a test PDF file with the given text content."""
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    doc.save(str(path))
    doc.close()
    return path

def assert_entity_supported(engine, entity_type, languages=None):
    """Assert that an entity type is supported in the given languages."""
    if languages is None:
        languages = LANGUAGES
    for language in languages:
        assert entity_type in engine.get_supported_entities(language=language), \
            f"Entity {entity_type} not supported in {language}"