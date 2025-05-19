import pytest

from processing.tests.test_utils import assert_entity_supported


@pytest.mark.unit
def test_organization_recognizer_supported_by_all_langs(setup_engine):
    assert_entity_supported(setup_engine, "ORGANIZATION")


@pytest.mark.unit
def test_org_recognizer(setup_engine):
    test_cases = [
        {"text": "He works at Google", "expected_entity": "ORGANIZATION"},
        {"text": "The event was sponsored by Microsoft.", "expected_entity": "ORGANIZATION"},
        {"text": "She is employed by the United Nations.", "expected_entity": "ORGANIZATION"},
        {"text": "My friend got a job at Red Cross.", "expected_entity": "ORGANIZATION"},
        {"text": "Apple released new products this year.", "expected_entity": "ORGANIZATION"},
    ]

    errors = []
    for case in test_cases:
        text = case["text"]
        expected_entity = case["expected_entity"]
        results = setup_engine.analyze(text=text, entities=[expected_entity], language="en")
        print(results)
        if not any(r.entity_type == expected_entity for r in results):
            errors.append(f"Expected entity '{expected_entity}' not found in: {text}")

    assert not errors, "\n".join(errors)
