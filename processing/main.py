from pathlib import Path
from pprint import pprint
from typing import List
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider, RecognizerResult
from config.config import CONFIG_DIRECTORY, FULL_CONFIG_FILE

def pp_analyzer_config(analyzer_engine: AnalyzerEngine):
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
    return analyzer_engine.analyze(text, language=lang,return_decision_process=True)

def pp_analyzer_results(file, results: List[RecognizerResult], text: str, print_decision_process=False):
    for result in results:
        output = f"\nPII-Detected: {result.entity_type} {text[result.start:result.end]}"
        print(output)
        file.write(output)
        if print_decision_process:
            output = f"\nDecision process {result.analysis_explanation.__dict__}"
            print(output)
            file.write(output)
        pprint(result)

if __name__ == "__main__":
    analyzer_config_path = Path.joinpath(Path(CONFIG_DIRECTORY), FULL_CONFIG_FILE)
    analyzer_engine = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_config_path).create_engine()
    pp_analyzer_config(analyzer_engine)
    
    # Analyze PII
    #text = "This is a testing document. We try to redact certain information here. My license plate is W-24681R. Name: Max Mustermann. E-Mail: Max.Mustermann@myserver.com. Tel.: +43 512 508 3399. Here weh ave some text. Let’s see if we can pull it from an document, that was exported via word to a PDF:"

    with open("text.txt", "r") as fin:
        text = fin.read()
        text1 = text[0:int(len(text)/2)]
        text2 = text[int(len(text)/2):]
        results1 = analyze_text(analyzer_engine, text1, lang="de")
        results2 = analyze_text(analyzer_engine, text2, lang="de")
        with open("output2.txt", "w+") as fout:
            pp_analyzer_results(fout, results1, text1)
            pp_analyzer_results(fout, results2, text2)

