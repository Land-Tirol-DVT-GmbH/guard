---
sidebar_position: 1
---
# Introduction

## 🚀 Overview

**Guard** is a powerful tool for detecting and redacting sensitive information from text and documents. Built on **Presidio**, it combines advanced natural language processing with customizable configurations for your specific needs.

Guard provides:
- **CLI Tool**: A command-line interface to process PDFs.
- **REST API**: A Flask server to analyze sensitive data programmatically.
- **Customizable Recognizers**: Tailor detection to your specific requirements.
- **Multilingual Support**: Detect sensitive data in English, German, Italian (Beta)

## 🌟 Advantages

### 1. Simplicity
<details>
<summary>Tap to expand: Rapid Setup, YAML Configuration, Pre-Configured</summary>

- **Rapid Setup**: Install and start using Guard in just a few minutes.
- **YAML Configuration**: Write your configurations naturally and include new recognizers at ease.
- **Pre-Configured**: Pre-configured with recognizers focused on Austrian data.
</details>

---

### 2. Powerfulness
<details>
<summary>Tap to expand: Custom Recognizers, Multiple Languages, Multiple Entities, Transformers</summary>
- **Custom Recognizers**: Define your own recognizers for unique use cases.
- **Multiple Languages**: Supports English, German, and Italian.
- **Multiple Entities**: Supports `PERSON`, `EMAIL`, `PHONE_NUMBER`, `LOCATION`, `ORGANIZATION`, `AUSTRIAN_LICENSE_PLATE`
- **Multiple NLP engines**: Builds on top of multiple NLP engines to gather the best results: Spacy, Flair NER, Distillbert 
</details>
---

## ✨ Show Me Examples

### Example 1: Simple PDF Processing with CLI
```bash
python guard_cli.py --file sensitive.pdf --output redacted/
```

### Example 2: Analyze Text with the REST API
Send a `POST` request to the `/analyze` endpoint:
```json
{
  "text": "Der Verantwortliche für die Kundenbetreuung in Innsbruck ist Johannes Mustermann",
  "language": "de",
}
```
The API will return:
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
    },
    {
        "analysis_explanation": null,
        "end": 80,
        "entity_type": "PERSON",
        "recognition_metadata": {
            "recognizer_identifier": "Flair Analytics_2190473762320",
            "recognizer_name": "Flair Analytics"
        },
        "score": 1.0,
        "start": 61
    }
]
```

---

## 💡 Documentation

Get started and explore more:
- [Getting Started Guide](docs/getting-started.md)
- [CLI Tool Guide](docs/cli-tool.md)
- [API Reference](docs/api-reference.md)
- [Analyzer Configuration](docs/analyzer-configuration.md)
- [Contributing Guide](docs/contributing.md)

---

## 🎉  Development

`GUARD` is developed under the company [DVT](https://www.dvt.at/) during the summer term of 2025.

### Contributors

| Contributor    |
|----------------|
| **Alan Insam** | 
| **Simon Muscatello**   |
| **Leto Ziegler** |

---

## 🔗 Useful Links
- [GitHub Repository](https://github.com/Land-Tirol-DVT-GmbH/guard)
- [Issues and Feature Requests](https://github.com/Land-Tirol-DVT-GmbH/guard/issues)