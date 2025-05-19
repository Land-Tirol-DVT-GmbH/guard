import pytest

from processing.tests.test_utils import get_expected_text

test_data_en = [
    {
        "text": "For further information, contact us at info@example.com.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 39, "end": 55}
        ]
    },
    {
        "text": "Please send your feedback to feedback@company.at before Friday.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 29, "end": 48}
        ]
    },
    {
        "text": "The invoice was sent from billing@dienstleister.de yesterday.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 26, "end": 50}
        ]
    },
    {
        "text": "You can reach him at mario.rossi@universita.it for academic inquiries.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 21, "end": 46}
        ]
    },
    {
        "text": "Contact our HR team via hr@globalenterprise.com anytime.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 24, "end": 47}
        ]
    },
    {
        "text": "Her email, anna.mueller@firma.de, was not working last week.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 11, "end": 32}
        ]
    },
    {
        "text": "Technical support is available at support@techhub.at during office hours.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 34, "end": 52}
        ]
    },
    {
        "text": "Please whitelist contact@trustedsource.com in your spam filter.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 17, "end": 42}
        ]
    },
    {
        "text": "Our legal team can be reached via legal@kanzlei.de.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 34, "end": 50}
        ]
    }
]


def verify_entity_recognition(engine, test_cases, language):
    errors = []
    for case in test_cases:
        text = case["text"]
        expected = case["expected"]
        expected_text = get_expected_text(case)
        results = engine.analyze(text, language=language)
        actual = [{"type": r.entity_type, "start": r.start, "end": r.end} for r in results]

        # handle order-independence
        expected_set = set(tuple(e.items()) for e in expected)
        actual_set = set(tuple(e.items()) for e in actual)

        if actual_set != expected_set:
            errors.append(
                f"Mismatch in {language} entity detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected}\n"
                f"Got      : {actual}\n"
                f"Expected text: {expected_text}\n"
            )
    return errors


@pytest.mark.unit
def test_email_recognizer_supported_by_all_langs(setup_engine):
    """Test that EMAIL_ADDRESS entity is supported in multiple languages."""
    supported_languages = ["it", "de", "en"]

    for language in supported_languages:
        assert "EMAIL_ADDRESS" in setup_engine.get_supported_entities(language=language)


@pytest.mark.unit
def test_email_recognizer_en(setup_engine):
    """Test email address recognition in English text."""
    errors = verify_entity_recognition(setup_engine, test_data_en, "en")
    assert not errors, "\n".join(errors)


