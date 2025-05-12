import pytest


# ----- VALID AUT_LICENSE_PLATE SAMPLES (German/Austrian Context) -----
# Examples use common Austrian district codes (I, W, IL, S, GU, ZE, KI, BL)
# and valid sequence formats (Number+Letters, Letters+Number, variations).
# Includes plates with spaces and hyphens.
pair_list_text_expected_response_de_at = [
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
       "text": "Ist das W1?", # Shortest possible format
       "expected": [
           {"type": "AUT_LICENSE_PLATE", "start": 8, "end": 10}
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
    """Extracts the expected text spans based on start/end indices."""
    return [entity['text'][e['start']:e['end']] for e in entity['expected']]

# --- Test Setup ---
@pytest.mark.unit
def test_aut_license_plate_recognizer_supported(setup_engine):
    """
    Check if AUT_LICENSE_PLATE recognizer is supported by the different langauges
    """
    assert "AUT_LICENSE_PLATE" in setup_engine.get_supported_entities(language="de")
    assert "AUT_LICENSE_PLATE" in setup_engine.get_supported_entities(language="it")
    assert "AUT_LICENSE_PLATE" in setup_engine.get_supported_entities(language="en")

@pytest.mark.unit
def test_valid_aut_license_plates_de_at(setup_engine):
    """Tests the recognizer against valid Austrian license plates in German text."""
    errors = []
    for case in pair_list_text_expected_response_de_at:
        text = case["text"]
        expected = case["expected"]
        # Analyze using the German language model
        results = setup_engine.analyze(text, language="de")
        filtered_results = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]
        expected_plates = [e for e in expected if e["type"] == "AUT_LICENSE_PLATE"]

        stripped = strip_scores(filtered_results)

        # Compare sets to ignore order
        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_plates):
            errors.append(
                f"Mismatch in German/Austrian AUT_LICENSE_PLATE detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_plates}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {get_expected_areas_of_text({'text': text, 'expected': expected_plates})}"
            )
    assert not errors, "\n---\n".join(errors)
    
# ----- VALID AUT_LICENSE_PLATE SAMPLES (English Context) -----
pair_list_text_expected_response_en = [
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
]


@pytest.mark.unit
def test_valid_aut_license_plates_en(setup_engine):
    """Tests the recognizer against valid Austrian license plates in English text."""
    errors = []
    for case in pair_list_text_expected_response_en:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language="en")
        filtered_results = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]
        expected_plates = [e for e in expected if e["type"] == "AUT_LICENSE_PLATE"]
        stripped = strip_scores(filtered_results)

        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_plates):
            errors.append(
                f"Mismatch in English AUT_LICENSE_PLATE detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_plates}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {get_expected_areas_of_text({'text': text, 'expected': expected_plates})}"
            )
    assert not errors, "\n---\n".join(errors)
    

# ----- VALID AUT_LICENSE_PLATE SAMPLES (Italian Context) -----
pair_list_text_expected_response_it = [
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
       "text": "La targa era BL45RD.", # No space/hyphen
       "expected": [
           {"type": "AUT_LICENSE_PLATE", "start": 13, "end": 19}
       ]
    }
]

@pytest.mark.unit
def test_valid_aut_license_plates_it(setup_engine):
    """Tests the recognizer against valid Austrian license plates in Italian text."""
    errors = []
    for case in pair_list_text_expected_response_it:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language="it")
        filtered_results = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]
        expected_plates = [e for e in expected if e["type"] == "AUT_LICENSE_PLATE"]
        stripped = strip_scores(filtered_results)

        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_plates):
            errors.append(
                f"Mismatch in Italian AUT_LICENSE_PLATE detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_plates}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {get_expected_areas_of_text({'text': text, 'expected': expected_plates})}"
            )
    assert not errors, "\n---\n".join(errors)



# ----- INVALID AUT_LICENSE_PLATE Test Cases (Trap Cases) -----
invalid_aut_license_plate_test_cases_de_at = [
    #"Das ist ein deutsches Kennzeichen: B-XY 123.", # German format
    #"München hat M-AA 4567 als Kennzeichen.", # German format
    #"Die Postleitzahl ist A-6020 Innsbruck.", # Postal code format
    "Produktcode: SKU 123 AB", # Product code similar format
    #"Das Modell ist W-45.", # Model number, not a plate
    "Ungültiges Format: W 123456", # Too many digits after letter
    "Kein Kennzeichen: XYZ 12 A", # Invalid district code
    "Unvollständig: I-", # Incomplete plate
    "Nur der Bezirkscode: Er kommt aus I.", # Just the district code
    "Firma G und GU Baustoffe", # Company name using possible codes
    #"Bitte Code WE 123 eingeben.", # Generic code
    #"Der Flug ist OS 201 nach Wien.", # Flight number (OS = Austrian Airlines)
    #"Die Bestellung lautet auf Artikel BL-45-RD.", # Article number
    "Nur Zahlen 123456 oder Buchstaben ABCDEF reichen nicht." # Only numbers/letters
]

@pytest.mark.unit
def test_invalid_aut_license_plates_de_at(setup_engine):
    """Tests that invalid or non-plate strings are not recognized as AUT_LICENSE_PLATE."""
    errors = []
    for case in invalid_aut_license_plate_test_cases_de_at:
        results = setup_engine.analyze(case, language="de")
        # No stripping needed here, just check if any result is of the wrong type
        plates_found = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]

        if plates_found:
            stripped = strip_scores(plates_found) # Strip for cleaner error message
            errors.append(
                f"Unexpected AUT_LICENSE_PLATE detected in German/Austrian text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    assert not errors, "\n---\n".join(errors)
    
invalid_aut_license_plate_test_cases_en = [
    #"This is a UK plate: AB12 CDE.", # UK format
    "Check the US plate format: XYZ 123?", # US format (example)
    #"The postal code is A-6020 for Innsbruck.", # Postal code
    "Product ID: SKU 123 AB", # Product code
    #"The model name is W-45 Turbo.", # Model name
    "Invalid format: W 1234567", # Too many digits
    "Not a plate: XYZ 12 A", # Invalid district code
    "Incomplete: I- registration", # Incomplete
    "He comes from I-Land province.", # Confusing word
    #"Please enter access code WE 123.", # Generic code
    #"Flight OS 201 to Vienna is on time.", # Flight number
    #"The order includes item BL-45-RD.", # Item number
    "Only numbers 123456 or letters ABCDEF are not enough." # Only numbers/letters
]

@pytest.mark.unit
def test_invalid_aut_license_plates_en(setup_engine):
    """Tests that invalid or non-plate strings are not recognized as AUT_LICENSE_PLATE in English."""
    errors = []
    for case in invalid_aut_license_plate_test_cases_en:
        results = setup_engine.analyze(case, language="en")
        plates_found = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]
        if plates_found:
            stripped = strip_scores(plates_found)
            errors.append(
                f"Unexpected AUT_LICENSE_PLATE detected in English text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    assert not errors, "\n---\n".join(errors)

invalid_aut_license_plate_test_cases_it = [
    #"Questa è una targa italiana: AA 123 BB.", # Italian format
    #"La targa tedesca era B XY 123.", # German format in Italian text
    "Il codice postale è 39100 Bolzano.", # Italian postal code
    "Codice prodotto: SKU 123 AB", # Product code
    #"Il modello dell'auto è W-45.", # Model name
    "Formato non valido: W 1234567", # Invalid format
    "Non è una targa: XYZ 12 A", # Invalid district code
    "Incompleto: I- per iniziare", # Incomplete
    "Viene dalla provincia di I-Landia.", # Confusing word/name
    #"Inserire il codice di accesso WE 123.", # Generic code
    #"Il volo OS 201 per Vienna è puntuale.", # Flight number
    #"L'ordine include l'articolo BL-45-RD.", # Item number
    "Solo numeri 123456 o lettere ABCDEF non bastano." # Only numbers/letters
]
    
    
@pytest.mark.unit
def test_invalid_aut_license_plates_it(setup_engine):
    """Tests that invalid or non-plate strings are not recognized as AUT_LICENSE_PLATE in Italian."""
    errors = []
    for case in invalid_aut_license_plate_test_cases_it:
        results = setup_engine.analyze(case, language="it")
        plates_found = [r for r in results if r.entity_type == "AUT_LICENSE_PLATE"]
        if plates_found:
            stripped = strip_scores(plates_found)
            errors.append(
                f"Unexpected AUT_LICENSE_PLATE detected in Italian text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    assert not errors, "\n---\n".join(errors)