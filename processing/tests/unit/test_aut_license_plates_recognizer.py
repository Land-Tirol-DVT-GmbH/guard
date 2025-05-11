import pytest


def strip_scores(results):
    """Convert RecognizerResult objects to dicts and strip scores for comparison."""
    return [
        {"type": r.entity_type, "start": r.start, "end": r.end}
        for r in results
    ]


def test_lp_recognizer_supported_by_all_langs(setup_engine):
    """
    Pattern recognizer (for entity AUT_LICENSE_PLATE) is supported by it, de, en
    """
    assert "AUT_LICENSE_PLATE" in setup_engine.get_supported_entities(language="it")
    assert "AUT_LICENSE_PLATE" in setup_engine.get_supported_entities(language="de")
    assert "AUT_LICENSE_PLATE" in setup_engine.get_supported_entities(language="en")


# ----- VALID LICENSE PLATE TESTS -----

def test_valid_license_plates_en(setup_engine):
    text = "I saw cars with plates W 12345A and G 6789BC on the road."
    results = setup_engine.analyze(text, language="en")
    expected = [
        {"type": "AUT_LICENSE_PLATE", "start": 23, "end": 31},
        {"type": "AUT_LICENSE_PLATE", "start": 36, "end": 44},
    ]
    assert strip_scores(results) == expected


def test_valid_license_plates_it(setup_engine):
    text = "Ho visto una macchina con la targa L 2947P."
    results = setup_engine.analyze(text, language="it")
    expected = [{"type": "AUT_LICENSE_PLATE", "start": 35, "end": 42}]
    assert strip_scores(results) == expected


def test_valid_license_plates_de(setup_engine):
    text = "Das Auto hatte das Kennzeichen S 170MZ."
    results = setup_engine.analyze(text, language="de")
    expected = [{"type": "AUT_LICENSE_PLATE", "start": 31, "end": 38}]
    assert strip_scores(results) == expected


# ----- INVALID LICENSE PLATE TESTS -----

def test_invalid_license_plate_en(setup_engine):
    text = "The car had a plate ABC 1234, which is not Austrian."
    results = setup_engine.analyze(text, language="en")
    assert strip_scores(results) == []


def test_invalid_license_plate_it(setup_engine):
    text = "La targa era XYZ 9876, non valida in Austria."
    results = setup_engine.analyze(text, language="it")
    assert strip_scores(results) == []


"""def test_invalid_license_plate_de(setup_engine):
    text = "Das Kennzeichen war QW 12345, was in Österreich ungültig ist."
    results = setup_engine.analyze(text, language="de")
    expected = []  # LOCATION might be detected though
    assert all(res.entity_type != "AUT_LICENSE_PLATE" for res in results)"""


# ----- ERROR CASE -----

def test_analyze_without_language(setup_engine):
    text = "Mein Kennzeichen ist KU 791 XR"
    with pytest.raises(TypeError):
        setup_engine.analyze(text)
