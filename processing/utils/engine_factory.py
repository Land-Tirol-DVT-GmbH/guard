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

    # Try to use GPU if possible, but handle missing dependencies gracefully
    use_gpu = False
    if not torch.cuda.is_available():
        try:
            # This sets the preference but doesn't guarantee GPU usage
            use_gpu = spacy.prefer_gpu()
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            spacy.require_gpu()
            print(f"CUDA is available. GPU will be used: {use_gpu}")
            if logger:
                logger.info("Running SpaCy on GPU: %s", use_gpu)
        except Exception as gpu_error:
            print(f"GPU requested but not available or dependencies missing: {gpu_error}")
            if logger:
                logger.warning(f"GPU requested but not available or dependencies missing: {gpu_error}")
            print("Falling back to CPU.")
            if logger:
                logger.info("Falling back to CPU.")
    else:
        print("CUDA is not available. CPU will be used.")
        if logger:
            logger.info("CUDA is not available. CPU will be used.")

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