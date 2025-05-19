import pytest

from processing.tests.test_utils import strip_scores, assert_entity_supported

VALID_LICENSE_PLATES = {
    "de": [
        {
            "text": "Das Auto mit dem Kennzeichen I 123 AB gehört Herrn Müller.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 29, "end": 37},
            ]
        },
        {
            "text": "Ich habe den Wagen W-4567 CX gesehen.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 19, "end": 28}
            ]
        },
        {
            "text": "Melden Sie bitte den Vorfall mit dem Kennzeichen IL 9 ZY bei der Polizei.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 49, "end": 56}
            ]
        },
        {
            "text": "Kennzeichen: ZE 789 FG",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 13, "end": 22}
            ]
        },
        {
            "text": "Er fährt einen GU 10 H.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 15, "end": 22}
            ]
        },
        {
            "text": "War das der KI-555 PP?",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 12, "end": 21}
            ]
        },
        {
            "text": "Mehrere Autos wurden gemeldet: W 1234 A, I 987 B und SL 5 C.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 31, "end": 39},
                {"type": "AUT_LICENSE_PLATE", "start": 41, "end": 48},
                {"type": "AUT_LICENSE_PLATE", "start": 53, "end": 59},
            ]
        },
        {
            "text": "Das Kennzeichen BL45RD war auf einem LKW.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 16, "end": 22}
            ]
        },
        {
            "text": "Ist das W1?",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 8, "end": 10}
            ]
        }
    ],
    "en": [
        {
            "text": "The car with the license plate I 123 AB belongs to Mr. Müller.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 31, "end": 39},
            ]
        },
        {
            "text": "I saw the vehicle W-4567 CX near the station.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 18, "end": 27}
            ]
        },
        {
            "text": "Please report the incident involving plate IL 9 ZY to the police.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 43, "end": 50}
            ]
        },
    ],
    "it": [
        {
            "text": "L'auto con targa I 123 AB è del Sig. Müller.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 17, "end": 25},
            ]
        },
        {
            "text": "Ho visto il veicolo W-4567 CX vicino alla stazione.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 20, "end": 29}
            ]
        },
        {
            "text": "Segnalare l'incidente con la targa IL 9 ZY alla polizia.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 35, "end": 42}
            ]
        },
        {
            "text": "Targhe austriache come S 1 e GU 10 H sono state viste.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 23, "end": 28},
                {"type": "AUT_LICENSE_PLATE", "start": 29, "end": 36}
            ]
        },
        {
            "text": "La targa era BL45RD.",
            "expected": [
                {"type": "AUT_LICENSE_PLATE", "start": 13, "end": 19}
            ]
        }
    ]
}

INVALID_LICENSE_PLATES = {
    "de": [
        "Produktcode: SKU 123 AB",  # Product code similar format
        "Ungültiges Format: W 123456",  # Too many digits after letter
        "Kein Kennzeichen: XYZ 12 A",  # Invalid district code
        "Unvollständig: I-",  # Incomplete plate
        "Nur der Bezirkscode: Er kommt aus I.",  # Just the district code
        "Firma G und GU Baustoffe",  # Company name using possible codes
        "Nur Zahlen 123456 oder Buchstaben ABCDEF reichen nicht."  # Only numbers/letters
    ],
    "en": [
        "Check the US plate format: XYZ 123?",  # US format (example)
        "Product ID: SKU 123 AB",  # Product code
        "Invalid format: W 1234567",  # Too many digits
        "Not a plate: XYZ 12 A",  # Invalid district code
        "Incomplete: I- registration",  # Incomplete
        "He comes from I-Land province.",  # Confusing word
        "Only numbers 123456 or letters ABCDEF are not enough."  # Only numbers/letters
    ],
    "it": [
        "Il codice postale è 39100 Bolzano.",  # Italian postal code
        "Codice prodotto: SKU 123 AB",  # Product code
        "Formato non valido: W 1234567",  # Invalid format
        "Non è una targa: XYZ 12 A",  # Invalid district code
        "Incompleto: I- per iniziare",  # Incomplete
        "Viene dalla provincia di I-Landia.",  # Confusing word/name
        "Solo numeri 123456 o lettere ABCDEF non bastano."  # Only numbers/letters
    ]
}

def run_license_plate_test(setup_engine, test_cases, language):
    """Run test against license plate test cases for specified language."""
    errors = []
    for case in test_cases:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language=language)
        filtered_results = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]
        expected_plates = [e for e in expected if e["type"] == "AUT_LICENSE_PLATE"]
        expected_text = [text[e['start']:e['end']] for e in expected_plates]
        stripped = strip_scores(filtered_results)

        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_plates):
            errors.append(
                f"Mismatch in {language} AUT_LICENSE_PLATE detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_plates}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {expected_text}"
            )
    assert not errors, "\n---\n".join(errors)


def run_invalid_license_plate_test(setup_engine, invalid_cases, language):
    """Test that invalid strings are not recognized as license plates."""
    errors = []
    for case in invalid_cases:
        results = setup_engine.analyze(case, language=language)
        plates_found = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]
        if plates_found:
            stripped = strip_scores(plates_found)
            errors.append(
                f"Unexpected AUT_LICENSE_PLATE detected in {language} text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    assert not errors, "\n---\n".join(errors)


@pytest.mark.unit
def test_aut_license_plate_recognizer_supported(setup_engine):
    assert_entity_supported(setup_engine, "AUT_LICENSE_PLATE")


# Define supported languages
SUPPORTED_LANGUAGES = ["de", "en", "it"]

def run_license_plate_test_functions():
    """
    Create test functions for license plate recognition across different languages.
    """

    @pytest.mark.unit
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_valid_license_plates(setup_engine, language):
        """Tests the recognizer against valid Austrian license plates in different languages."""
        run_license_plate_test(setup_engine, VALID_LICENSE_PLATES[language], language)

    @pytest.mark.unit
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_invalid_license_plates(setup_engine, language):
        """Tests that invalid strings are not recognized as AUT_LICENSE_PLATE in different languages."""
        run_invalid_license_plate_test(setup_engine, INVALID_LICENSE_PLATES[language], language)

    return test_valid_license_plates, test_invalid_license_plates


test_valid_aut_license_plates, test_invalid_aut_license_plates = run_license_plate_test_functions()

