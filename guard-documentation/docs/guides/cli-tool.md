---
sidebar_position: 2
---

# CLI Tool

:::info

The CLI tool (`guard_cli.py`) provides a user-friendly command-line interface for processing PDF files, performing automated redaction or highlighting using Presidio, and interacting with the Guard system.
:::

## Overview

`guard_cli.py` is designed for processing sensitive PDFs in batch or individually. It leverages [Presidio](https://microsoft.github.io/presidio/) for PII detection, supports multiple languages, and now offers enhanced annotation and logging features.

The tool supports:
- Automated redaction **or** highlighting of PII in PDF documents.
- Per-page JSON logging of Presidio API input/output for audit or debugging.
- Health checks for the underlying Presidio API.
- Flexible file and directory input/output handling.
- Multi-language support.

---

## Features

<details>
<summary>Tap to expand: PDF Processing</summary>

- **Parsing PDF files**: Extracts the text layer from PDF files using [PyMuPDF](https://github.com/pymupdf/PyMuPDF), preparing them for PII analysis.
- **Automated PII Redaction or Highlighting**: 
  - By default, detected PII is **redacted** (blacked out) in the output PDF.
  - You can instead **highlight** detected PII using `--highlight` for review or QA purposes.
- **Batch Processing**: Supports processing multiple files at once by specifying a directory.
- **Output Naming**: 
  - Redacted files are saved with the prefix `REDACTED_` in the chosen output directory.
  - Highlighted files are saved with the prefix `HIGHLIGHTED_` in the output directory (defaults to `./highlighted_redaction/`).
- **Custom Redaction via JSON Input**:
  - Use `--json-input <dir>` to apply redactions directly from existing JSON metadata, bypassing backend PII detection.
  - The argument must point to a **directory** containing per-page redaction files named like `page_0.json`, `page_1.json`, etc.
  - Example usage: `-i redacted/LOGS_filename -f filename.pdf`  
    This expects a matching PDF file (`filename.pdf`) and a folder (`redacted/LOGS_filename/`) with the page-wise JSON files.
  - Useful for reprocessing with previously exported redaction metadata generated via JSON logging.
</details>

<details>
<summary>Tap to expand: Language Support</summary>

- **Supported Languages**: German (`de`), English (`en`), and Italian (`it`).
- **Default Language**: If not specified, defaults to German (`de`).
- **Custom Language Selection**: Use the `--language` option to select among the supported languages.
- **Display**: The CLI provides user-friendly language names and codes for clarity.
- **Validation**: The tool checks for unsupported languages and exits with a clear message if needed.
</details>

<details>
<summary>Tap to expand: API Health Check</summary>

- **Startup Health Check**: On every run, the CLI checks if the configured Presidio API endpoint is reachable and healthy before processing documents.
- **Error Handling**: If the API is unavailable, the tool exits and prints the error reason.
</details>

<details>
<summary>Tap to expand: File & Output Handling</summary>

- **Flexible Input**: Accepts either a single file (`--file`) or an entire directory (`--directory`) containing PDF files.
- **Validation**: Checks file and directory existence and ensures files are PDFs before processing.
- **Output Directory**:
  - You can specify where output files will be saved using `--output`.
  - Defaults:
    - Redacted: `./redacted/`
    - Highlighted: `./highlighted_redaction/`
- **Log Output**:
  - If JSON logging is enabled, logs are saved per PDF in a subdirectory named `<inputfilename>_LOGS/`, with one JSON file per page.
</details>

<details>
<summary>Tap to expand: JSON Logging (New)</summary>

- **Per-Page Logs**: Use `-j` or `--json-log` to save input and output from each Presidio API call per page.
- **Highlight Mode Implies Logging**: If `--highlight` is used, logging is automatically enabled.
- **Log Structure**: For each page, a JSON file captures the input request and Presidio's response.
- **Log Location**: Logs are stored in a folder named `<PDF_STEM>_LOGS` inside the chosen output directory.
</details>

---

## Usage

### Required Environment Setup

- Ensure a `.env` file is present in the same directory as `guard_cli.py` and contains a valid `PRESIDIO_API_ENDPOINT`.
- Required dependencies: `requests`, `PyMuPDF`, `python-dotenv`, and the project's `utils.file_handler` module.

### Command-Line Arguments

```bash
python guard_cli.py [OPTIONS]
```

#### Common Options

- `-f, --file`: Path to a PDF file to process.
- `-d, --directory`: Path to a directory containing one or more PDF files to redact/highlight.
- `-o, --output`: Directory where the output files will be saved.  
  - Defaults to `./redacted/` (redaction mode) or `./highlighted_redaction/` (highlight mode).
- `-l, --language`: Language for Presidio analysis. Supported: German (`de`), English (`en`), Italian (`it`). Defaults to `de`.
- `-j, --json-log`: Enable JSON logging. Saves Presidio input/output logs per page.
- `--highlight`: Instead of redacting, highlight detected PII. Implies JSON logging.

#### Example: Process a Single File with Redaction

```bash
python guard_cli.py --file /path/to/input.pdf --output /path/to/redacted/
```

#### Example: Process All PDFs in a Directory, Highlighting Instead of Redacting

```bash
python guard_cli.py --directory /path/to/pdf-directory --highlight
```

#### Example: Set Language and Enable JSON Logging

```bash
python guard_cli.py --file sample.pdf --language it --json-log
```

---

## Output

- **Redacted Files**: Saved in the output directory, prefixed with `REDACTED_`.
- **Highlighted Files**: Saved in the output directory, prefixed with `HIGHLIGHTED_` (when `--highlight` is used).
- **JSON Logs**: If enabled, per-page logs are stored in a folder named `<inputfilename>_LOGS/` in the output directory. Each page's log is `page_<n>.json` containing both the API request and response.

---

## Error Handling & Validation

- If the Presidio API is unreachable, the script will print an error and exit.
- If an unsupported language is specified, you’ll receive a clear message and the script will terminate.
- If both `--file` and `--directory` are omitted, the CLI will prompt for required input and exit.
- The tool validates that input files are PDFs and input paths exist.

---

## Example Workflow

```bash
python guard_cli.py --file sample.pdf --output redacted/
```
- Checks the health of the Presidio API.
- Loads `sample.pdf` and extracts its text.
- Analyzes for PII using Presidio (in German, by default).
- Detected PII is redacted (or highlighted if `--highlight` is set).
- The resulting file is saved as `redacted/REDACTED_sample.pdf`.
- If JSON logging is enabled, logs are saved in `redacted/sample_LOGS/page_0.json`, etc.

---

## Additional Notes

- Redaction is performed **in-place** using PyMuPDF, and is irreversible.
- You can process multiple files at once by pointing to a directory.
- Highlighted mode is ideal for QA or reviewing PII detection before irreversible redaction.
- The tool uses a modular approach and relies on the `FileHandler` class in `utils/file_handler.py` for input management.
- For troubleshooting, ensure that the `.env` file is present and the Presidio API endpoint is correctly set.

---