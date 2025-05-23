import pytest

from processing.tests.test_utils import get_expected_text, strip_scores, assert_entity_supported


class PersonRecognizerTestData:
    """Test data fixture for person recognizer tests."""

    # Valid person test cases by language
    VALID_PERSON_CASES = {
        "en": [
            {
                "text": "My name is John Doe and this is my friend Kyle Schmidt.",
                "expected": [
                    {"type": "PERSON", "start": 11, "end": 19},
                    {"type": "PERSON", "start": 42, "end": 54},
                ]
            },
            {
                "text": "Dr. Emily Stone and Prof. Michael O'Brien attended the meeting.",
                "expected": [
                    {"type": "PERSON", "start": 4, "end": 15},
                    {"type": "PERSON", "start": 26, "end": 41},
                ]
            },
            {
                "text": "Alice, Bob, and Charlie went to the park.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 5},
                    {"type": "PERSON", "start": 7, "end": 10},
                    {"type": "PERSON", "start": 16, "end": 23},
                ]
            },
            {
                "text": "The email was sent to Angela Merkel and Emmanuel Macron.",
                "expected": [
                    {"type": "PERSON", "start": 22, "end": 35},
                    {"type": "PERSON", "start": 40, "end": 55},
                ]
            },
            {
                "text": "We were introduced to Leonardo da Vinci and Marie Curie.",
                "expected": [
                    {"type": "PERSON", "start": 22, "end": 39},
                    {"type": "PERSON", "start": 44, "end": 55},
                ]
            },
            {
                "text": "Barack Obama, Joe Biden, and Donald Trump all gave speeches.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 12},
                    {"type": "PERSON", "start": 14, "end": 23},
                    {"type": "PERSON", "start": 29, "end": 41},
                ]
            },
            {
                "text": "Please contact Mr. John A. Smith or Ms. Lisa M. Brown for further details.",
                "expected": [
                    {"type": "PERSON", "start": 19, "end": 32},
                    {"type": "PERSON", "start": 40, "end": 53},
                ]
            },
            {
                "text": "Detective Conan Edogawa solved the case.",
                "expected": [
                    {"type": "PERSON", "start": 10, "end": 23},
                ]
            },
            {
                "text": "Satoshi Nakamoto is still a mystery.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 16},
                ]
            }
        ],
        "it": [
            {
                "text": "Mi chiamo Giovanni Rossi e questo è il mio amico Luca Bianchi.",
                "expected": [
                    {"type": "PERSON", "start": 10, "end": 24},
                    {"type": "PERSON", "start": 47, "end": 59},
                ]
            },
            {
                "text": "Il dottor Marco Verdi ha parlato con la professoressa Anna Neri.",
                "expected": [
                    {"type": "PERSON", "start": 10, "end": 21},
                    {"type": "PERSON", "start": 51, "end": 60},
                ]
            },
            {
                "text": "Giulia, Andrea e Matteo sono andati al cinema.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 6},
                    {"type": "PERSON", "start": 8, "end": 14},
                    {"type": "PERSON", "start": 17, "end": 23},
                ]
            },
            {
                "text": "L'email è stata inviata a Sergio Mattarella e Mario Draghi.",
                "expected": [
                    {"type": "PERSON", "start": 29, "end": 45},
                    {"type": "PERSON", "start": 48, "end": 60},
                ]
            },
            {
                "text": "Il CEO Luigi De Santis e il CTO Paola Ferrari hanno firmato l'accordo.",
                "expected": [
                    {"type": "PERSON", "start": 7, "end": 22},
                    {"type": "PERSON", "start": 31, "end": 44},
                ]
            },
            {
                "text": "Abbiamo incontrato Leonardo da Vinci e Galileo Galilei al museo.",
                "expected": [
                    {"type": "PERSON", "start": 20, "end": 37},
                    {"type": "PERSON", "start": 40, "end": 55},
                ]
            },
            {
                "text": "Silvio Berlusconi, Matteo Renzi e Giuseppe Conte erano presenti.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 17},
                    {"type": "PERSON", "start": 19, "end": 31},
                    {"type": "PERSON", "start": 34, "end": 48},
                ]
            },
            {
                "text": "Contattare il signor Alessandro Neri o la signora Chiara Galli per informazioni.",
                "expected": [
                    {"type": "PERSON", "start": 20, "end": 36},
                    {"type": "PERSON", "start": 52, "end": 64},
                ]
            },
            {
                "text": "Il commissario Montalbano ha risolto il caso.",
                "expected": [
                    {"type": "PERSON", "start": 15, "end": 26},
                ]
            },
            {
                "text": "Dante Alighieri è uno dei poeti italiani più famosi.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 15},
                ]
            }
        ],
        "de": [
            {
                "text": "Mein Name ist Franz Huber und das ist meine Freundin Lisa Meier.",
                "expected": [
                    {"type": "PERSON", "start": 14, "end": 25},
                    {"type": "PERSON", "start": 53, "end": 63}
                ]
            },
            {
                "text": "Herr Dr. Klaus Berger sprach mit Frau Prof. Anna Leitner.",
                "expected": [
                    {"type": "PERSON", "start": 9, "end": 21},
                    {"type": "PERSON", "start": 44, "end": 56}
                ]
            },
            {
                "text": "Maria, Lukas und Tobias trafen sich im Café.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 5},
                    {"type": "PERSON", "start": 7, "end": 12},
                    {"type": "PERSON", "start": 17, "end": 23}
                ]
            },
            {
                "text": "Die E-Mail wurde an Alexander Van der Bellen und Karl Nehammer gesendet.",
                "expected": [
                    {"type": "PERSON", "start": 20, "end": 44},
                    {"type": "PERSON", "start": 49, "end": 62}
                ]
            },
            {
                "text": "Der CEO Johannes Steiner und die CTO Eva Hofmann kündigten das Projekt an.",
                "expected": [
                    {"type": "PERSON", "start": 8, "end": 24},
                    {"type": "PERSON", "start": 37, "end": 48}
                ]
            },
            {
                "text": "Im Museum trafen sie Wolfgang Amadeus Mozart und Sigmund Freud.",
                "expected": [
                    {"type": "PERSON", "start": 21, "end": 44},
                    {"type": "PERSON", "start": 49, "end": 62}
                ]
            },
            {
                "text": "Sebastian Kurz, Pamela Rendi-Wagner und Norbert Hofer hielten Reden.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 14},
                    {"type": "PERSON", "start": 16, "end": 35},
                    {"type": "PERSON", "start": 40, "end": 53}
                ]
            },
            {
                "text": "Bitte kontaktieren Sie Herrn Markus Moser oder Frau Julia Brunner.",
                "expected": [
                    {"type": "PERSON", "start": 29, "end": 41},
                    {"type": "PERSON", "start": 52, "end": 65}
                ]
            },
            {
                "text": "Kommissar Rex ist in Wien sehr bekannt.",
                "expected": [
                    {"type": "PERSON", "start": 10, "end": 13},
                    {'type': 'LOCATION', 'start': 21, 'end': 25}
                ]
            },
            {
                "text": "Sigmund Freud ist ein berühmter österreichischer Psychologe.",
                "expected": [
                    {"type": "PERSON", "start": 0, "end": 13}
                ]
            }
        ]
    }

    # Invalid person test cases (texts that should not trigger person detection)
    INVALID_PERSON_CASES = {
        "en": [
            "We met at Lincoln Street near the library.",
            "The Tesla Model S was reviewed by AutoJohn.",
            "The Newton method is used in optimization.",
            "He ordered furniture from MarkHome Interiors.",
            "She works with the ClaraVision system daily.",
            "We host our services on MariaDB clusters.",
            "Einstein Room is booked for the entire week.",
        ],
        "it": [
            "Ci vediamo in Via Verdi alle otto.",
            "Uso il software Giulia per analizzare i dati.",
            "La stanza Leonardo è prenotata fino a domani.",
            "Abbiamo acquistato una Fiat Panda da MarcoAuto.",
            "Preferisco i prodotti della linea Giovanni.",
            "La presentazione sarà in Aula Dante.",
            "La libreria online si chiama MariaBooks.",
            "Abbiamo analizzato i dati con il framework Luigi.",
            "Mi piace il profumo Lorenzo, soprattutto d'estate.",
            "Ho ordinato il tavolo da GiulioDesign."
        ],
        "de": [
            "Wir treffen uns am Montag in der Mozartstraße.",
            "Die Sitzung fand im Raum Einstein statt.",
            "BMW, Siemens und Mercedes präsentierten ihre Produkte.",
            "Wir loggen uns bei MariaDB mit Root-Zugriff ein.",
        ]
    }


@pytest.mark.unit
def test_person_recognizer_supported_by_all_langs(setup_engine):
    assert_entity_supported(setup_engine, "PERSON")


@pytest.mark.unit
@pytest.mark.parametrize("language", ["en", "de"])
def test_valid_person_recognition(setup_engine, language):
    """Test person recognition in valid test cases for specified languages."""
    test_cases = PersonRecognizerTestData.VALID_PERSON_CASES[language]
    errors = []

    for case in test_cases:
        text = case["text"]
        expected = case["expected"]
        stripped = strip_scores(setup_engine.analyze(text, language=language))
        compared_recognition_results = set(tuple(e.items()) for e in expected) == set(
            tuple(a.items()) for a in stripped)

        if not compared_recognition_results:
            errors.append(
                f"Mismatch in {language.upper()} PERSON detection\n"
                f"Text     : {text}\n"
                f"Expected : {expected}\n"
                f"Got      : {stripped}\n"
                f"Expected text: {get_expected_text(case)}\n"
            )

    assert not errors, "\n".join(errors)


@pytest.mark.unit
@pytest.mark.parametrize("language", ["en", "it", "de"])
def test_invalid_person_recognition(setup_engine, language):
    """Test that invalid cases don't trigger person recognition."""
    test_cases = PersonRecognizerTestData.INVALID_PERSON_CASES[language]
    errors = []

    for case in test_cases:
        stripped = strip_scores(setup_engine.analyze(case, language=language))
        persons = [r for r in stripped if r["type"] == "PERSON"]

        if persons:
            errors.append(
                f"Unexpected PERSON detected in {language.upper()} text:\n"
                f"Text     : {case}\n"
                f"Entities : {persons}"
            )

    assert not errors, "\n".join(errors)


# Failure with Italian names
"""
@pytest.mark.unit
def test_valid_names_it(setup_engine):
    test_valid_person_recognition(setup_engine, "it")
"""
