import os
from pathlib import Path
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider, LemmaContextAwareEnhancer
from core.flair_recognizer import FlairRecognizer


def create_analyzer_engine() -> AnalyzerEngine:
    # Fetch the configuration file
    analyzer_conf_file = os.environ.get("ANALYZER_CONF_FILE")
    
    # Make sure the path is valid
    if not Path(analyzer_conf_file).exists():
        raise Exception(f"Configuration file {analyzer_conf_file} not found!")

    engine = AnalyzerEngineProvider(
        analyzer_engine_conf_file=analyzer_conf_file,
    ).create_engine()

    # Add the context enhancer
    engine.context_aware_enhancer = LemmaContextAwareEnhancer(
        context_prefix_count=10,
        context_suffix_count=10,
    )

    # Add Flair recognizers
    supported_languages = ["en", "de"]
    for lang in supported_languages:
        recognizer = FlairRecognizer(supported_language=lang)
        engine.registry.add_recognizer(recognizer)

    return engine
