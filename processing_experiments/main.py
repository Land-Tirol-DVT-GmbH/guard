from pprint import pprint
from typing import List
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider, RecognizerResult
from config.config import create_full_config
from config.flair_recognizer import FlairRecognizer

def pp_analyzer_config(analyzer_engine: AnalyzerEngine):
    """
    Pretty prints the analyzer engine configuration (Analyzer, NLP engine, Recognizers)
    
    Args:
        analyzer_engine (AnalyzerEngine): For which the config is pretty printed
    """
    for lang in ("de", "it", "en"):
        pprint(f"Supported entities for {lang}:")
        print("\n")
        pprint(analyzer_engine.get_supported_entities(lang), compact=True)

        print(f"\nLoaded recognizers for {lang}:")
        pprint([rec.name for rec in analyzer_engine.registry.get_recognizers(lang, all_fields=True)], compact=True)
        print("\n")

    print(f"\nLoaded NER models:")
    pprint(analyzer_engine.nlp_engine.models)
    

def analyze_text(analyzer_engine: AnalyzerEngine, text: str, lang:str):
    """
    Analyzes the text using the provided analyzer_engine
    
    Args:
        analyzer_engine (AnalyzerEngine): Presidio analyzer engine
        text(str): Text where the prediction is run
        lang(str): Language of the provided text
    """
    return analyzer_engine.analyze(text, language=lang,return_decision_process=True)

def pp_analyzer_results(results: List[RecognizerResult], text: str, print_decision_process=False):
    """
    Pretty prints the results of the analyzer engine run on the provided text
    
    Args:
        results (List[RecognizerResult]): Results returned by the Presidio Analyzer Engine
        text (str): Text associated with the results
        print_decision_process (bool): Dictates whether the analyzer engine shall print which recognizers detected the entities
    """
    for result in results:
        print(f"\nPII-Detected: {result.entity_type} {text[result.start:result.end]}")
        if print_decision_process:
            print(f"\nDecision process {result.analysis_explanation.__dict__}")
        pprint(result)

if __name__ == "__main__": 
    
    # Create a full config file for the given model
    full_config_path = create_full_config("distillbert")
    
    # Set up the engine
    analyzer_engine = AnalyzerEngineProvider(analyzer_engine_conf_file=full_config_path).create_engine()
    flair_recognizer = (
        FlairRecognizer(supported_language="en"),
        FlairRecognizer(supported_language="de")
    )
    analyzer_engine.registry.add_recognizer(flair_recognizer[0])
    analyzer_engine.registry.add_recognizer(flair_recognizer[1])
    
    pp_analyzer_config(analyzer_engine)
    
    # Analyze PII
    text_en = "This is a testing document. My surname is Mustermann. My full name is George Rosemary. We try to redact certain information here. My license plate is W-24681R. My name is Max Mustermann. E-Mail: Max.Mustermann@myserver.com. Tel.: +43 512 508 3399. Here weh ave some text. Let’s see if we can pull it from an document, that was exported via word to a PDF:"
    text_de = "Dies ist ein Testdokument. Mein Nachname ist Mustermann. Mein Name ist Martin Mustermann. Wir versuchen hier, bestimmte Informationen zu schwärzen. Mein Kennzeichen ist W-24681R. Mein Name ist Max Mustermann. E-Mail: Max.Mustermann@myserver.com. Tel.: +43 512 508 3399. Hier haben wir etwas Text. Mal sehen, ob wir ihn aus einem Dokument extrahieren können, das über Word in ein PDF exportiert wurde:"
    text_it = "Questo è un documento di prova. Il mio cognome è Mustermann. Cerchiamo di oscurare alcune informazioni qui. La mia targa è W-24681R. Il mio nome è Max Mustermann. E-mail: Max.Mustermann@myserver.com. Tel.: +43 512 508 3399. Qui abbiamo del testo. Vediamo se riusciamo a estrarlo da un documento esportato da Word in PDF:"
    
    pprint("Starting analyzing:")
    results = analyze_text(analyzer_engine, text_en, lang="en")
    pp_analyzer_results(results, text_en, print_decision_process=True)

