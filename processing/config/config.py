import yaml
from pathlib import Path

# CONSTANTS
CONFIG_DIRECTORY = "config"
ANALYZER_CONFIG_FILE = "analyzer_config.yaml"
RECOGNIZER_REGISTRY_CONFIG_FILE = "recognizer_registry_config.yaml"
NLP_ENGINE_CONFIG_FILE = "transformers_nlp_engine_config.yaml"
FULL_CONFIG_FILE = "full_analyzer_config.yaml"

# Collect the configs
config_files = [ANALYZER_CONFIG_FILE, RECOGNIZER_REGISTRY_CONFIG_FILE, NLP_ENGINE_CONFIG_FILE]
configs = {}

# Iterate over all config files
for config_file in config_files:
    path_to_config = Path.joinpath(Path(CONFIG_DIRECTORY), config_file)
    with open(path_to_config, 'r') as file:
        configs.update(yaml.safe_load(file))


# Write the merged configuration to a new YAML file
with open(Path.joinpath(Path(CONFIG_DIRECTORY), FULL_CONFIG_FILE), 'w') as file:
    yaml.dump(configs, file, default_flow_style=False)
