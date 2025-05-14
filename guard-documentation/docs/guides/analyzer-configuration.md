---
sidebar_position : 4
---

# Analyzer Configuration

The `full_analyzer_config.yaml` file defines the pipeline for detecting and redacting sensitive data.

## Key Components

### `default_score_threshold`
- The minimum confidence score for detecting entities. Default: `0.4`.

### `nlp_configuration`
#### Engines
- **SpaCy**: Lightweight NLP model for entity detection.
- **Transformers**: Deep learning model for complex PII detection.

#### Supported Languages
- **English (`en`)**
- **German (`de`)**
- **Italian (`it`)**

#### NER Configuration
- `aggregation_strategy`: Combines overlapping results (`simple` by default).
- `alignment_mode`: Aligns tokens (`expand` by default).

### Recognizer Registry
- **Predefined Recognizers**:
  - `EmailRecognizer`: Detects email addresses.
  - `PhoneRecognizer`: Detects phone numbers.
- **Custom Recognizers**:
  - `AUTLicensePlateRecognizer`: Detects Austrian license plates.

### Supported Languages
- `en`, `de`, `it`: Fully supported for detection and redaction.