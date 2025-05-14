---
sidebar_position: 2
---

# Getting Started

Follow these steps to set up and run Guard:

## Prerequisites

Ensure that you have the following installed:
- Python 3.8 or higher
- Conda (Anaconda or Miniconda)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-repo>/guard.git
   cd guard
   ```

2. Create a Conda environment:
   ```bash
   conda create --name guard-env python=3.8 -y
   ```

3. Activate the environment:
   ```bash
   conda activate guard-env
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure the server:
   - Edit the `full_analyzer_config.yaml` file to suit your requirements.

## Running the Application

### Start the REST API Server
Run the Flask server:
```bash
python app.py
```

### Use the CLI Tool
Run the CLI tool to process files:
```bash
python guard_cli.py --input /path/to/input.pdf --output /path/to/output
```

Visit the [CLI Tool Documentation](cli-tool.md) for more details.

## Running Tests

Run the test suite to ensure everything works as expected:
```bash
pytest
```

## Deactivating the Environment
When you're done working, deactivate the Conda environment:
```bash
conda deactivate
```