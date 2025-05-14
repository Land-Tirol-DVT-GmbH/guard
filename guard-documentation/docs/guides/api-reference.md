---
sidebar_position: 3
---

# API Reference

The REST API server (`app.py`) provides endpoints for analyzing text and managing recognizers.

## Endpoints

### `/analyze`
- **Description**: Processes text to detect sensitive information.
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "text": "Your input text here",
    "language": "en",
    "entities": ["EMAIL_ADDRESS", "PHONE_NUMBER"]
  }
  ```
- **Response**:
  ```json
  {
    "analyzeResults": [
      {
        "entityType": "EMAIL_ADDRESS",
        "start": 10,
        "end": 25,
        "score": 0.98
      }
    ]
  }
  ```

### `/supportedentities`
- **Description**: Lists all supported PII entity types.
- **Method**: `GET`
- **Response**:
  ```json
  ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"]
  ```

### `/recognizers`
- **Description**: Lists available recognizers for a given language.
- **Method**: `GET`
- **Query Parameters**:
  - `language`: Language code (e.g., `en`).
- **Response**:
  ```json
  ["EmailRecognizer", "PhoneRecognizer"]
  ```

### `/health`
- **Description**: Checks the API's availability.
- **Method**: `GET`
- **Response**:
  ```json
  {"status": "healthy"}
  ```

## Example Usage
See the [CLI Tool Documentation](cli-tool.md) for how the CLI interacts with these endpoints.