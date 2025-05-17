---
sidebar_position: 4
---

# Analyzer Configuration

:::info
The `full_analyzer_config.yaml` file defines the detailed pipeline and settings for detecting and redacting sensitive data (PII) using the GUARD system.
:::

## Key Components

### `default_score_threshold`
- **Description**: The minimum confidence score required for an entity to be considered as detected.
- **Default**: `0.4`
- Entities with a score below this threshold are ignored.

---

### `nlp_configuration`

#### Models per Language
- Specifies which NLP models are used for each supported language.
- **English (`en`)**:
  - `spacy`: `en_core_web_lg`
  - `transformers`: `yonigo/distilbert-base-multilingual-cased-pii`
- **German (`de`)**:
  - `spacy`: `de_core_news_lg`
  - `transformers`: `yonigo/distilbert-base-multilingual-cased-pii`
- **Italian (`it`)**:
  - `spacy`: `it_core_news_lg`
  - `transformers`: `yonigo/distilbert-base-multilingual-cased-pii`

#### NER Model Configuration
- `aggregation_strategy`: How overlapping entities are merged; set to `simple`.
- `alignment_mode`: Token alignment strategy for entity spans; set to `expand`.
- `labels_to_ignore`: Labels/entities to ignore.
- `low_confidence_score_multiplier`: Multiplier applied to entities in `low_score_entity_names`.
- `low_score_entity_names`: List of entities to which the low confidence multiplier applies.
- `model_to_presidio_entity_mapping`: Maps model-specific labels to Presidio entity types.  
  Example mappings:
  - `CITY` → `LOCATION`
  - `EMAIL` → `EMAIL_ADDRESS`
  - `GIVENNAME1`, `GIVENNAME2` → `PERSON`
  - `TEL` → `PHONE_NUMBER`
  - And more.
- `stride`: Controls the sliding window step for NER models; set to `16`.
- `nlp_engine_name`: Name of the respective NLP engine.

---

### Recognizer Registry

Defines the recognizers available for PII detection, including both predefined and custom recognizers.

- **Recognizers**:
  - **Predefined Recognizers**:
    - `EmailRecognizer`: Detects emails, with language-specific context for German (`email`, `kontakt`), Italian (`email`, `contatto`), and English.
    - `PhoneRecognizer`: Detects phone numbers in English, German, and Italian.
  - **Custom Recognizers**:
    - `AUTLicensePlateRecognizer`: Uses regex to detect Austrian license plates.  
      - Entity: `AUT_LICENSE_PLATE`
      - Context words for German (`kennzeichen`, `fahrzeug`, `kfz`), Italian (`targa`, `veicolo`, `auto`), and English (`license`, `plate`, `vehicle`, `car`).

#### Recognizer Types
- `type: predefined`: Built-in recognizers for common entities.
- `type: custom`: Project-specific recognizers using custom patterns.

---

### Supported Languages

The system is fully configured for the following languages:
- **German (`de`)**
- **Italian (`it`)**
- **English (`en`)**

All three languages are supported for entity recognition and redaction, with language-specific models and recognizers.

---

## Example: Entity Mapping

| Model Label   | Mapped Presidio Entity |
|---------------|-----------------------|
| CITY          | LOCATION              |
| EMAIL         | EMAIL_ADDRESS         |
| GIVENNAME1    | PERSON                |
| TEL           | PHONE_NUMBER          |
| ...           | ...                   |

---

## Notes

- Changing the configuration file allows for easy extension or modification of supported languages, models, and recognizers.
- Context words improve entity detection by providing additional clues, especially for custom recognizers.
- The threshold and multiplier settings allow for fine-tuning detection sensitivity, particularly for ambiguous entities.

For detailed configuration, on how to customize the given configuration, adding more / other NLP engines, patters etc. visit the [Microsoft Presidio No Code Documentation](https://microsoft.github.io/presidio/tutorial/08_no_code/).