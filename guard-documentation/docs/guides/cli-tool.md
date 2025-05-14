---
sidebar_position: 2
---

# CLI Tool

The CLI tool (`guard_cli.py`) provides a simple interface for processing files and interacting with the Guard system.

## Features
1. **PDF Processing**:
   - Processes PDF files and redacts sensitive information.
2. **Language Support**:
   - Supports German (`de`), English (`en`), and Italian (`it`).
3. **API Health Check**:
   - Verifies if the API server is reachable.

## Usage

### Commands

#### Process a File
```bash
python guard_cli.py --input /path/to/input.pdf --output /path/to/output
```

#### Check API Health
```bash
python guard_cli.py --health
```

### Options
- `--input`: Path to the file you want to process.
- `--output`: Path to save the redacted file.
- `--health`: Check the API server's availability.

## Example
```bash
python guard_cli.py --input sample.pdf --output redacted/
```

This will save the redacted file in the `redacted/` directory with the prefix `REDACTED_`.