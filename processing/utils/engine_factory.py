from logging import Logger
import os
from pathlib import Path
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider, LemmaContextAwareEnhancer
import spacy
import torch
from core.flair_recognizer import FlairRecognizer


def create_analyzer_engine(logger: Logger=None) -> AnalyzerEngine:
    analyzer_conf_file = os.environ.get("ANALYZER_CONF_FILE")

    project_root = os.environ.get("PROJECT_ROOT")
    if project_root:
        resolved_path = Path(project_root) / analyzer_conf_file
    else:
        base_dir = Path(__file__).parent.parent
        resolved_path = base_dir / analyzer_conf_file

    # Make sure the path is valid
    if not resolved_path.exists():
        raise Exception(f"Configuration file {resolved_path} not found!")

    # Check if CUDA is available and prefer the GPU in spacy
    if torch.cuda.is_available():
       use_gpu = spacy.prefer_gpu()
       if logger: logger.info("Running SpaCy on GPU: %s", use_gpu)

    engine = AnalyzerEngineProvider(
        analyzer_engine_conf_file=str(resolved_path),
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
