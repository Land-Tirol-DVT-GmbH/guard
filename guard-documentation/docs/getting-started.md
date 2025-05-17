---
sidebar_position: 2
---

# Getting Started
:::info

Follow this guide on how to setup the CLI tool or the GUARD server
:::

---

## 📚 Prerequisites

Ensure that you have the following installed:
- Python 3.8 or higher
- Conda (Anaconda or Miniconda)

---

## 1. Installation
Set up GUARD in a few minutes:

1. Clone the repository:
   ```bash
   git clone https://github.com/Land-Tirol-DVT-GmbH/guard.git && cd guard/processing
   ```

2. Install dependencies:
   ```bash
   conda env create -f environment.yml && conda activate guard-env
   ```

---

## 2. Running the Application

### 1. Start the REST API Server
Run the Flask API server for local inference:
   ```bash
   python app.py
   ```

Expand for more details in the [API Reference](guides/api-reference.md).

### 2. Use the CLI Tool
Run the CLI tool to process files:
   ```bash
   python guard_cli.py --file /path/to/input.pdf --output /path/to/output
   ```

Expand for more details in the [CLI Reference](guides/cli-tool.md).

---

## 3. Running Tests

Run the test suite to ensure everything works as expected:
```bash
pytest
```

## 4. Deactivating the Environment
When you're done working, deactivate the Conda environment:
```bash
conda deactivate
```