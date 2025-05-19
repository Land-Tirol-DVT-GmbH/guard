import pytest

from processing.tests.test_utils import strip_scores, assert_entity_supported

TEST_DATA_PHONE_DE = [
    {
        "text": "Kontakt International: +43 1 555 0 888 (Wien).",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 23, "end": 38}  # +43 1 555 0 888
        ]
    },
    {
        "text": "Innsbrucker IKB Unternehmen hat Nummer 0800 500502.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 39, "end": 50}  # 0800 500502
        ]
    },
    {
        "text": "Notfallnummer Schweiz: +41 44 987 65 43",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 23, "end": 39}  # +41 44 987 65 43
        ]
    },
    {
        "text": "Wichtige Nummer: +1-212-555-0199 (USA)",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 17, "end": 32}  # +1-212-555-0199
        ]
    },
    {
        "text": "Italienische Nummer unter +39 338 3751985 erreichbar.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 26, "end": 41}  # 338 3751985
        ]
    }
]

INVALID_PHONE_TEST_CASES_DE = [
    "Die Postleitzahl ist 6020.",  # Too short, clearly a PLZ
    "Im Jahr 2024 war das anders.",  # Year
    "Kennzeichen W 123 AB",  # License plate
    "Artikelnummer 0512-AB",  # Contains letters
    "Nur Vorwahl: 0664",  # Incomplete
    "Bitte nur Ziffern 123 eingeben.",  # Too short
    "Es kostet 50 Euro.",  # Price
    "Flug OS 201",  # Flight number
    "Die Temperatur ist +15 Grad.",  # Measurement
]

TEST_DATA_PHONE_EN = [
    {
        "text": "International contact: +43-1-555-0-888 (Vienna office).",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 23, "end": 38}  # +43-1-555-0-888
        ]
    },
    {
        "text": "Swiss emergency contact: +41 44 987 65 43.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 25, "end": 41}  # +41 44 987 65 43
        ]
    },
    {
        "text": "Important US number: +1 (212) 555-0199.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 21, "end": 38}  # +1 (212) 555-0199
        ]
    },
    {
        "text": "Italian Hotline +390211223344 is available 24/7.",  # No spaces
        "expected": [
            {"type": "PHONE_NUMBER", "start": 16, "end": 29}  # +390211223344
        ]
    }
]

INVALID_PHONE_TEST_CASES_EN = [
    "The ZIP code is 90210.",  # Too short / ZIP code format
    "Account number: 1234567890123",  # Long number, context
    "It happened in 2023.",  # Year
    "License plate S 123 XX",  # License plate
    "Item code 0664-XYZ",  # Contains letters
    "Just the area code: 0512",  # Incomplete
    "Enter the 3 digits.",  # Too short
    "The price is $50.",  # Price
    "Flight BA 202",  # Flight number
    "Temperature: +20 C",  # Measurement
    "Order # 123-456",  # Order number format
]

TEST_DATA_PHONE_IT = [
    {
        "text": "Chiamaci al 0512 / 123 456 per informazioni su Innsbruck.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 12, "end": 26}  # 0512 / 123 456
        ]
    },
    {
        "text": "Contatto internazionale: +43 1 555 0 888 (ufficio Vienna).",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 25, "end": 40}  # +43 1 555 0 888
        ]
    },
    {
        "text": "Disponibile Lu-Ve al 0676 / 33 44 555 o numero tedesco +49 89 123456.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 21, "end": 37},  # 0676 / 33 44 555
            {"type": "PHONE_NUMBER", "start": 55, "end": 68}  # +49 89 123456
        ]
    },
    {
        "text": "Contatto emergenza Svizzera: +41 44 987 65 43.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 29, "end": 45}  # +41 44 987 65 43
        ]
    },
    {
        "text": "Numero USA importante: +1-212-555-0199.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 23, "end": 38}  # +1-212-555-0199
        ]
    },
    {
        "text": "Hotline Italiana +39 335 1122334 disponibile.",  # Italian mobile
        "expected": [
            {"type": "PHONE_NUMBER", "start": 17, "end": 32}  # +39 335 1122334
        ]
    }
]

INVALID_PHONE_TEST_CASES_IT = [
    "Il CAP è 39100.",  # CAP = Italian Postal Code
    "Numero di conto: 123456789012",  # Bank account number
    "È successo nel 2022.",  # Year
    "Targa auto W 123 AB",  # License plate
    "Codice articolo 0512-CD",  # Contains letters
    "Solo il prefisso: 06",  # Incomplete Italian prefix
    "Inserisci 5 cifre.",  # Too short
    "Il costo è 50 €.",  # Price
    "Volo AZ 604",  # Flight number (Alitalia)
    "La temperatura è +25 gradi.",  # Measurement
    "Ordine n. 123/456",  # Order number format
]

TEST_DATA_MAPPING = {
    "de": {
        "test_data": TEST_DATA_PHONE_DE,
        "invalid_cases": INVALID_PHONE_TEST_CASES_DE
    },
    "en": {
        "test_data": TEST_DATA_PHONE_EN,
        "invalid_cases": INVALID_PHONE_TEST_CASES_EN
    },
    "it": {
        "test_data": TEST_DATA_PHONE_IT,
        "invalid_cases": INVALID_PHONE_TEST_CASES_IT
    }
}

def run_phone_detection_test(setup_engine, test_data, language):
    """Centralized test implementation for phone number detection across languages.

    Args:
        setup_engine: The recognition engine fixture
        test_data: List of test cases with text and expected results
        language: Language code to use for analysis

    Returns:
        List of error messages (empty if all tests pass)
    """
    errors = []
    for case in test_data:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language=language)

        stripped = strip_scores([r for r in results if r.entity_type == "PHONE_NUMBER"])
        expected_numbers = [e for e in expected if e["type"] == "PHONE_NUMBER"]
        expected = [text[e['start']:e['end']] for e in expected_numbers]

        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_numbers):
            errors.append(
                f"Mismatch in {language.upper()} PHONE_NUMBER detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_numbers}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {expected}"
            )
    return errors


def run_invalid_phone_test(setup_engine, test_cases, language):
    """Centralized test implementation for validating that invalid patterns are not recognized.

    Args:
        setup_engine: The recognition engine fixture
        test_cases: List of text samples that should not trigger detection
        language: Language code to use for analysis

    Returns:
        List of error messages (empty if all tests pass)
    """
    errors = []
    for case in test_cases:
        results = setup_engine.analyze(case, language=language)
        phones_found = [r for r in results if r.entity_type == "PHONE_NUMBER"]

        if phones_found:
            stripped = [{"type": r.entity_type, "start": r.start, "end": r.end} for r in phones_found]
            errors.append(
                f"Unexpected PHONE_NUMBER detected in {language.upper()} text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    return errors

# Tests
@pytest.mark.unit
def test_phone_number_recognizer_supported_by_all_langs(setup_engine):
    assert_entity_supported(setup_engine, "PHONE_NUMBER")

@pytest.mark.unit
@pytest.mark.parametrize("language", TEST_DATA_MAPPING.keys())
def test_phone_number_recognition(setup_engine, language):
    """Test phone number recognition for valid cases across all supported languages."""
    errors = run_phone_detection_test(
        setup_engine, 
        TEST_DATA_MAPPING[language]["test_data"], 
        language
    )
    assert not errors, "\n---\n".join(errors)

@pytest.mark.unit
@pytest.mark.parametrize("language", TEST_DATA_MAPPING.keys())
def test_invalid_phone_number_recognition(setup_engine, language):
    """Test phone number recognition for invalid cases across all supported languages."""
    errors = run_invalid_phone_test(
        setup_engine, 
        TEST_DATA_MAPPING[language]["invalid_cases"], 
        language
    )
    assert not errors, "\n---\n".join(errors)

