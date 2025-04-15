import yaml
from pathlib import Path

# CONSTANTS
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # Goes up from config/ to root
CONFIG_DIRECTORY = PROJECT_ROOT / "config"
CONFIG_FILES_DIRECTORY = CONFIG_DIRECTORY / "files"

ANALYZER_CONFIG_FILE = "analyzer_config.yaml"
RECOGNIZER_REGISTRY_CONFIG_FILE = "recognizer_registry_config.yaml"
NLP_ENGINES_CONFIG_FILES = {
    "spacy": "spacy_engine_config.yaml",
    "stanza": "stanza_engine_config.yaml",
    "piiranha": "piiranha_transformer_engine_config.yaml",
    "distillbert": "distillbert_transfomer_config.yaml",
}

FULL_CONFIG_FILE = "full_analyzer_config.yaml"

def create_full_config(model_name: str, output_file: str = FULL_CONFIG_FILE) -> Path:
    """
    Merges base analyzer config, recognizer config, and selected NLP engine config
    into one YAML file for Presidio analyzer.

    Args:
        model_name (str): The key for the NLP engine config (e.g. 'distillbert', 'spacy').
        output_file (str): Output file name for the full merged config.

    Returns:
        Path: Path to the created full config file.

    Raises:
        ValueError: If the given model_name is not supported.
        FileNotFoundError: If any of the config files are missing.
    """
    if model_name not in NLP_ENGINES_CONFIG_FILES:
        raise ValueError(f"Unsupported model name '{model_name}'. Available: {list(NLP_ENGINES_CONFIG_FILES)}")

    config_files = [
        ANALYZER_CONFIG_FILE,
        RECOGNIZER_REGISTRY_CONFIG_FILE,
        NLP_ENGINES_CONFIG_FILES[model_name],
    ]

    merged_config = {}
    for file_name in config_files:
        config_path = Path(CONFIG_FILES_DIRECTORY) / file_name
        if not config_path.exists():
            raise FileNotFoundError(f"Missing config file: {config_path}")
        with open(config_path, "r") as f:
            merged_config.update(yaml.safe_load(f))

    output_path = Path(CONFIG_FILES_DIRECTORY) / output_file
    with open(output_path, "w") as f:
        yaml.dump(merged_config, f, default_flow_style=False)

    return output_path
