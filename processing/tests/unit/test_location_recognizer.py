import pytest

from processing.tests.test_utils import strip_scores, assert_entity_supported, get_expected_text

test_data_en = [
    {
        "text": "I live in Vienna.",
        "expected": [
            {"type": "LOCATION", "start": 10, "end": 16}  # Vienna
        ]
    },
    {
        "text": "My address is 1010 Vienna, Austria.",
        "expected": [
            {"type": "LOCATION", "start": 19, "end": 25},  # Vienna
            {"type": "LOCATION", "start": 27, "end": 34}  # Austria
        ]
    },
    {
        "text": "We are based in Milan, Italy.",
        "expected": [
            {"type": "LOCATION", "start": 16, "end": 21},  # Milan
            {"type": "LOCATION", "start": 23, "end": 28}  # Italy
        ]
    },
    {
        "text": "He moved to Berlin.",
        "expected": [
            {"type": "LOCATION", "start": 12, "end": 18}  # Berlin
        ]
    },
    {
        "text": "Send the postcard to my house in Innsbruck.",
        "expected": [
            {"type": "LOCATION", "start": 33, "end": 42}  # Innsbruck
        ]
    },
    {
        "text": "I am from Tyrol.",
        "expected": [
            {"type": "LOCATION", "start": 10, "end": 15}  # Tyrol
        ]
    }
]


@pytest.mark.unit
def test_location_recognizer_supported_by_all_langs(setup_engine):
    assert_entity_supported(setup_engine, "LOCATION")


@pytest.mark.unit
def test_location_recognizer_en(setup_engine):
    """Test that the location recognizer correctly identifies locations in text with proper spans."""
    errors = []

    for case in test_data_en:
        text = case["text"]
        expected = case["expected"]

        entities_to_analyze = list(set(entity["type"] for entity in expected))

        results = setup_engine.analyze(text=text, entities=entities_to_analyze, language="en")
        stripped = strip_scores(results)

        expected_set = set(tuple(e.items()) for e in expected)
        actual_set = set(tuple(e.items()) for e in stripped)

        if expected_set != actual_set:
            expected_spans = get_expected_text(case)
            extracted_spans = [text[e["start"]:e["end"]] for e in stripped]

            errors.append(
                f"Mismatch in location detection\n"
                f"Text: {text}\n"
                f"Expected entities: {expected}\n"
                f"Expected spans: {expected_spans}\n"
                f"Got entities: {stripped}\n"
                f"Got spans: {extracted_spans}\n"
            )

    assert not errors, "\n".join(errors)
