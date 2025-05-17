---
sidebar_position: 3
---

# API Reference

The REST API server (`app.py`) provides endpoints for analyzing text and managing entity recognizers, forming the backend for PII detection and redaction in the GUARD system.

---

## Endpoints

### `POST /analyze`

- **Description**:  
  Analyzes submitted text for sensitive information (PII) and returns detected entities.

- **Request Body**:  
  ```json
  {
    "text": "Your input text here",
    "language": "en"
  }
  ```
  - `text` (**required**): The text to be analyzed for PII.
  - `language` (**required**): Language code (e.g., `de`, `en`, `it`).  
  - *(Note: The `entities` field is not currently supported and will be ignored if provided.)*

- **Response**:  
  Returns a JSON array, where each element describes a detected entity:
  ```json
  [
    {
      "analysis_explanation": null,
      "end": 56,
      "entity_type": "LOCATION",
      "recognition_metadata": {
        "recognizer_identifier": "Flair Analytics_2190473762320",
        "recognizer_name": "Flair Analytics"
      },
      "score": 1.0,
      "start": 47
    }
  ]
  ```
  - `entity_type`: The type of PII detected (e.g., `EMAIL_ADDRESS`, `LOCATION`).
  - `start`, `end`: Character offsets in the input text where the entity was found.
  - `score`: Confidence score of the detection.
  - `recognition_metadata`: Metadata about the recognizer that detected the entity, including its identifier and name.
  - `analysis_explanation`: Additional analysis details (currently `null` unless explanation is enabled).

- **Error Responses**:
  - `400 Bad Request`: Missing or malformed input (e.g., missing `text` or `language`).
  - `500 Internal Server Error`: Server-side processing error.

---

### `GET /supportedentities`

- **Description**:  
  Returns a list of all supported PII entity types for the specified language.

- **Query Parameters**:
  - `language`: Language code to filter supported entities.

- **Response**:  
  ```json
  ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "LOCATION", "AUSTRIAN_LICENSE_PLATE", "ORGANIZATION"]
  ```

---

### `GET /recognizers`

- **Description**:  
  Returns a list of all recognizers available for a given language.

- **Query Parameters**:
  - `language`: Language code to filter recognizers.

- **Response**:  
  ```json
  ["EmailRecognizer", "PhoneRecognizer", ...]
  ```

---

### `GET /health`

- **Description**:  
  Checks if the API server is running and reachable.

- **Response**:  
  Returns a plain text message:
  ```
  Presidio Analyzer service is up
  ```

---

## Example Usage

See the [CLI Tool Documentation](cli-tool.md) for practical examples of interacting with these endpoints.

---

## Notes

- All error responses are returned as JSON in the format:  
  ```json
  { "error": "Error message here" }
  ```
- The API is designed for internal use and expects requests from trusted components, such as the CLI tool or orchestrated pipelines.
- For more information about how the endpoints are implemented, see [`processing/app.py`](https://github.com/Land-Tirol-DVT-GmbH/guard/blob/main/processing/app.py).