import pytest

def strip_scores(results):
    """Convert RecognizerResult objects to dicts and strip scores for comparison."""
    return [
        {"type": r.entity_type, "start": r.start, "end": r.end}
        for r in results
    ]

def get_expected_areas_of_text(entity):
    """Extracts the expected text spans based on start/end indices."""
    return [entity['text'][e['start']:e['end']] for e in entity['expected']]

@pytest.mark.unit
def test_phone_number_recognizer_supported_by_all_langs(setup_engine):
    """
    Check if PHONE_NUMBER recognizer is supported by it, de, en.
    """
    assert "PHONE_NUMBER" in setup_engine.get_supported_entities(language="it")
    assert "PHONE_NUMBER" in setup_engine.get_supported_entities(language="de")
    assert "PHONE_NUMBER" in setup_engine.get_supported_entities(language="en")

# ----- VALID PHONE_NUMBER TESTS (German/Austrian Context) -----
test_data_phone_de = [
    {
        "text": "Kontakt International: +43 1 555 0 888 (Wien).",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 23, "end": 38} # +43 1 555 0 888
        ]
    },
    {
        "text": "Innsbrucker IKB Unternehmen hat Nummer 0800 500502.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 39, "end": 50} # 0800 500502
        ]
    },
    {
       "text": "Notfallnummer Schweiz: +41 44 987 65 43",
       "expected": [
           {"type": "PHONE_NUMBER", "start": 23, "end": 39} # +41 44 987 65 43
       ]
    },
    {
       "text": "Wichtige Nummer: +1-212-555-0199 (USA)",
       "expected": [
           {"type": "PHONE_NUMBER", "start": 17, "end": 32} # +1-212-555-0199
       ]
    },
    {
       "text": "Italienische Nummer unter +39 338 3751985 erreichbar.",
       "expected": [
            {"type": "PHONE_NUMBER", "start": 26, "end": 41} # 338 3751985
        ]
    }
]

@pytest.mark.unit
def test_phone_number_de(setup_engine):
    """Tests PHONE_NUMBER recognizer in German context."""
    errors = []
    for case in test_data_phone_de:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language="de")
        # Filter results for PHONE_NUMBER only for comparison
        filtered_results = [r for r in results if r.entity_type == "PHONE_NUMBER"]
        expected_numbers = [e for e in expected if e["type"] == "PHONE_NUMBER"]
        stripped = strip_scores(filtered_results)

        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_numbers):
            errors.append(
                f"Mismatch in German PHONE_NUMBER detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_numbers}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {get_expected_areas_of_text({'text': text, 'expected': expected_numbers})}"
            )
    assert not errors, "\n---\n".join(errors)

# ----- INVALID PHONE_NUMBER Test Cases (German/Austrian Context) -----
invalid_phone_test_cases_de = [
    "Die Postleitzahl ist 6020.", # Too short, clearly a PLZ
    "Im Jahr 2024 war das anders.", # Year
    "Kennzeichen W 123 AB", # License plate
    "Artikelnummer 0512-AB", # Contains letters
    "Nur Vorwahl: 0664", # Incomplete
    "Bitte nur Ziffern 123 eingeben.", # Too short
    "Es kostet 50 Euro.", # Price
    "Flug OS 201", # Flight number
    "Die Temperatur ist +15 Grad.", # Measurement
]

@pytest.mark.unit
def test_invalid_phone_number_de(setup_engine):
    """Tests that invalid or non-phone numbers are not recognized in German."""
    errors = []
    for case in invalid_phone_test_cases_de:
        results = setup_engine.analyze(case, language="de")
        phones_found = [r for r in results if r.entity_type == "PHONE_NUMBER"]
        if phones_found:
            stripped = strip_scores(phones_found)
            errors.append(
                f"Unexpected PHONE_NUMBER detected in German text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    assert not errors, "\n---\n".join(errors)


# ----- VALID PHONE_NUMBER TESTS (English Context) -----
test_data_phone_en = [
    {
        "text": "International contact: +43-1-555-0-888 (Vienna office).",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 23, "end": 38} # +43-1-555-0-888
        ]
    },
    {
       "text": "Swiss emergency contact: +41 44 987 65 43.",
       "expected": [
           {"type": "PHONE_NUMBER", "start": 25, "end": 41} # +41 44 987 65 43
       ]
    },
    {
       "text": "Important US number: +1 (212) 555-0199.",
       "expected": [
           {"type": "PHONE_NUMBER", "start": 21, "end": 38} # +1 (212) 555-0199
       ]
    },
    {
       "text": "Italian Hotline +390211223344 is available 24/7.", # No spaces
       "expected": [
            {"type": "PHONE_NUMBER", "start": 16, "end": 29} # +390211223344
        ]
    }
]

@pytest.mark.unit
def test_phone_number_en(setup_engine):
    """Tests PHONE_NUMBER recognizer in English context."""
    errors = []
    for case in test_data_phone_en:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language="en")
        filtered_results = [r for r in results if r.entity_type == "PHONE_NUMBER"]
        expected_numbers = [e for e in expected if e["type"] == "PHONE_NUMBER"]
        stripped = strip_scores(filtered_results)

        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_numbers):
            errors.append(
                f"Mismatch in English PHONE_NUMBER detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_numbers}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {get_expected_areas_of_text({'text': text, 'expected': expected_numbers})}"
            )
    assert not errors, "\n---\n".join(errors)

# ----- INVALID PHONE_NUMBER Test Cases (English Context) -----
invalid_phone_test_cases_en = [
    "The ZIP code is 90210.", # Too short / ZIP code format
    "Account number: 1234567890123", # Long number, context
    "It happened in 2023.", # Year
    "License plate S 123 XX", # License plate
    "Item code 0664-XYZ", # Contains letters
    "Just the area code: 0512", # Incomplete
    "Enter the 3 digits.", # Too short
    "The price is $50.", # Price
    "Flight BA 202", # Flight number
    "Temperature: +20 C", # Measurement
    "Order # 123-456", # Order number format
]

@pytest.mark.unit
def test_invalid_phone_number_en(setup_engine):
    """Tests that invalid or non-phone numbers are not recognized in English."""
    errors = []
    for case in invalid_phone_test_cases_en:
        results = setup_engine.analyze(case, language="en")
        phones_found = [r for r in results if r.entity_type == "PHONE_NUMBER"]
        if phones_found:
            stripped = strip_scores(phones_found)
            errors.append(
                f"Unexpected PHONE_NUMBER detected in English text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    assert not errors, "\n---\n".join(errors)


# ----- VALID PHONE_NUMBER TESTS (Italian Context) -----
test_data_phone_it = [
    {
        "text": "Chiamaci al 0512 / 123 456 per informazioni su Innsbruck.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 12, "end": 26} # 0512 / 123 456
        ]
    },
    {
        "text": "Contatto internazionale: +43 1 555 0 888 (ufficio Vienna).",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 25, "end": 40} # +43 1 555 0 888
        ]
    },
    {
        "text": "Disponibile Lu-Ve al 0676 / 33 44 555 o numero tedesco +49 89 123456.",
        "expected": [
            {"type": "PHONE_NUMBER", "start": 21, "end": 37}, # 0676 / 33 44 555
            {"type": "PHONE_NUMBER", "start": 55, "end": 68}  # +49 89 123456
        ]
    },
    {
       "text": "Contatto emergenza Svizzera: +41 44 987 65 43.",
       "expected": [
           {"type": "PHONE_NUMBER", "start": 29, "end": 45} # +41 44 987 65 43
       ]
    },
    {
       "text": "Numero USA importante: +1-212-555-0199.",
       "expected": [
           {"type": "PHONE_NUMBER", "start": 23, "end": 38} # +1-212-555-0199
       ]
    },
    {
       "text": "Hotline Italiana +39 335 1122334 disponibile.", # Italian mobile
       "expected": [
            {"type": "PHONE_NUMBER", "start": 17, "end": 32} # +39 335 1122334
        ]
    }
]

@pytest.mark.unit
def test_phone_number_it(setup_engine):
    """Tests PHONE_NUMBER recognizer in Italian context."""
    errors = []
    for case in test_data_phone_it:
        text = case["text"]
        expected = case["expected"]
        results = setup_engine.analyze(text, language="it")
        filtered_results = [r for r in results if r.entity_type == "PHONE_NUMBER"]
        expected_numbers = [e for e in expected if e["type"] == "PHONE_NUMBER"]
        stripped = strip_scores(filtered_results)

        if set(tuple(e.items()) for e in stripped) != set(tuple(e.items()) for e in expected_numbers):
            errors.append(
                f"Mismatch in Italian PHONE_NUMBER detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected_numbers}\n"
                f"Got      : {stripped}\n"
                f"Expected ranges return: {get_expected_areas_of_text({'text': text, 'expected': expected_numbers})}"
            )
    assert not errors, "\n---\n".join(errors)

# ----- INVALID PHONE_NUMBER Test Cases (Italian Context) -----
invalid_phone_test_cases_it = [
    "Il CAP è 39100.", # CAP = Italian Postal Code
    "Numero di conto: 123456789012", # Bank account number
    "È successo nel 2022.", # Year
    "Targa auto W 123 AB", # License plate
    "Codice articolo 0512-CD", # Contains letters
    "Solo il prefisso: 06", # Incomplete Italian prefix
    "Inserisci 5 cifre.", # Too short
    "Il costo è 50 €.", # Price
    "Volo AZ 604", # Flight number (Alitalia)
    "La temperatura è +25 gradi.", # Measurement
    "Ordine n. 123/456", # Order number format
]

@pytest.mark.unit
def test_invalid_phone_number_it(setup_engine):
    """Tests that invalid or non-phone numbers are not recognized in Italian."""
    errors = []
    for case in invalid_phone_test_cases_it:
        results = setup_engine.analyze(case, language="it")
        phones_found = [r for r in results if r.entity_type == "PHONE_NUMBER"]
        if phones_found:
            stripped = strip_scores(phones_found)
            errors.append(
                f"Unexpected PHONE_NUMBER detected in Italian text:\n"
                f"Text     : {case}\n"
                f"Entities : {stripped}"
            )
    assert not errors, "\n---\n".join(errors)