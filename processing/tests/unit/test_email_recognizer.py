import pytest

test_data_en = [
    {
        "text": "For further information, contact us at info@example.com.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 39, "end": 55}  # info@example.com
        ]
    },
    {
        "text": "Please send your feedback to feedback@company.at before Friday.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 29, "end": 48}  # feedback@company.at
        ]
    },
    {
        "text": "The invoice was sent from billing@dienstleister.de yesterday.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 26, "end": 50}  # billing@dienstleister.de
        ]
    },
    {
        "text": "You can reach Mario at mario.rossi@universita.it for academic inquiries.",
        "expected": [
            {'type': 'EMAIL_ADDRESS', 'start': 23, 'end': 48}, # mario.rossi@universita.it
            {'type': 'PERSON', 'start': 14, 'end': 19}  
        ]
    },
    {
        "text": "Contact our HR team via hr@globalenterprise.com anytime.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 24, "end": 47}  # hr@globalenterprise.com
        ]
    },
    {
        "text": "Her email, anna.mueller@firma.de, was not working last week.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 11, "end": 32}  # anna.mueller@firma.de
        ]
    },
    {
        "text": "Technical support is available at support@techhub.at during office hours.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 34, "end": 52}  # support@techhub.at
        ]
    },
    {
        "text": "Please whitelist contact@trustedsource.com in your spam filter.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 17, "end": 42}  # contact@trustedsource.com
        ]
    },
    {
        "text": "Our legal team can be reached via legal@kanzlei.de.",
        "expected": [
            {"type": "EMAIL_ADDRESS", "start": 34, "end": 50}  # legal@kanzlei.de
        ]
    }
]

def strip_scores(results):
    """Convert RecognizerResult objects to dicts and strip scores for comparison."""
    return [
        {"type": r.entity_type, "start": r.start, "end": r.end}
        for r in results
    ]

def get_expected_areas_of_text(entity):
    return [entity['text'][e['start']:e['end']] for e in entity['expected']]

@pytest.mark.unit
def test_lp_recognizer_supported_by_all_langs(setup_engine):
    """
    Pattern recognizer (for entity PERSON) is supported by it, de, en
    """
    assert "EMAIL_ADDRESS" in setup_engine.get_supported_entities(language="it")
    assert "EMAIL_ADDRESS" in setup_engine.get_supported_entities(language="de")
    assert "EMAIL_ADDRESS" in setup_engine.get_supported_entities(language="en")

@pytest.mark.unit
def test_email_recognizer_en(setup_engine):
    errors = []
    for case in test_data_en:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language="en")
        stripped = strip_scores(results)
        
        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in case["expected"]):
            errors.append(
                f"Mismatch in English PERSON detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected}\n"
                f"Got      : {stripped}\n"
                f"expected range returns:{get_expected_areas_of_text(case)}\n"
            )
    assert not errors, "\n".join(errors)