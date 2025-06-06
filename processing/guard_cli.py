import os
import sys
import json
import argparse
from typing import List, Dict, Any
from pathlib import Path
import requests
from utils.file_handler import FileHandler
from dotenv import load_dotenv

DEFAULT_LANGUAGE="de"

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

presidio_api_endpoint = os.environ.get("PRESIDIO_API_ENDPOINT")
presidio_api_analysis = presidio_api_endpoint + "/analyze"

used_language = DEFAULT_LANGUAGE

LANGUAGES_DISPLAY = {
    "de": "German",
    "en": "English",
    "it": "Italian"
}

#TODO: Verbose mode maybe?

#check if presidio is available
def check_api_available(api_endpoint: str):
    """Checks if the refered Presidio-API endpoint is available."""
    try:
        response = requests.get(api_endpoint + "/health")
        if response.status_code != 200:
            print(f"Presidio service not available! Received:", response.status_code)
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Could not reach presidio service: {e}")
        sys.exit(1)

def add_redaction_annotation_to_page(page, areas):
    for area in areas:
        page.add_redact_annot(area, fill=(0, 0, 0))

def add_highlight_annotation_to_page(page, areas):
    for area in areas:
        page.add_highlight_annot(area)

def process_presidio_results(results, page, text, should_redact=True, verbose = False):
    """
    Apply redaction annotations to a PDF page based on Presidio analysis results

    Args:
        results (List[Dict]): List of recognized PII entities, each with 'start' and 'end' offsets.
        page (fitz.Page): The PDF page object from PyMuPDF to apply redactions on.
        text (str): Full text content of the page, used to locate entities.
        should_redact (bool): If True, redact. If False, highlight. Defaults to True.
        verbose (bool): If True, print messages for not-found text. Defaults to False.
    """
    if not results:
        return

    annotation_fn = add_redaction_annotation_to_page if should_redact else add_highlight_annotation_to_page

    for entity in results:
        matched_text = text[entity["start"]:entity["end"]]
        areas = page.search_for(matched_text)

        if not areas:
            if verbose:
                print(f"Text '{matched_text}' not found for redaction on this page.")
            continue

        annotation_fn(page=page, areas=areas)

    if should_redact:
        page.apply_redactions()

def process_pdf(pdf, generate_log=False, verbose=False, should_redact=True) -> List[Dict[str, Any]]:
    """
    Analyze and redact sensitive information in a single PDF file using Presidio.

    Args:
        pdf (fitz.Document): A PyMuPDF document object representing the input PDF.
        generate_log: Generates a log dictionary for each page of the pdf.
        verbose: If True, prints detailed processing information.
        should_redact: If Ture, redacts the document, if False, highlights whatever would be redacted.

    Returns:
        List:[{"page": count starting at 0, "request": request body, "response": presidio response body}]
    """

    logs = []
    count = 0
    pdf_name = Path(pdf.name).name
    print("Processing: " + pdf_name)
    for page in pdf:
        text = page.get_text()
        built_request = {
            "text": text,
            "language": used_language
        }
        response = requests.post(presidio_api_analysis, json=built_request)
        if generate_log:
            logs.append({"page": count, "request": built_request, "response": response.json()})


        if response.status_code != 200:
            print(f"Presidio error for: {pdf_name} ")
            print(response.text)
            continue

        results = response.json()
        process_presidio_results(results=results, page=page, text=text, should_redact=should_redact)
        count += 1
    return logs

def process_pdf_with_json(pdf, json_dir, verbose=False, should_redact=True) -> None:
    """
    Redact sensitive information in a single PDF file using a JSON input file instead of Presidio API.

    Args:
        pdf (fitz.Document): A PyMuPDF document object representing the input PDF.
        json_dir (Path): Path to the directory containing JSON files with redaction information.
        verbose: If True, prints detailed processing information.
        should_redact: If True, redacts the document, if False, highlights whatever would be redacted.
    """
    count = 0
    pdf_name = Path(pdf.name).name
    print("Processing:" + pdf_name + " with JSON input")

    for page in pdf:
        json_file = json_dir / f"page_{count}.json"

        if not json_file.exists():
            print(f"Warning: JSON file {json_file} not found for page {count}. Skipping this page.")
            count += 1
            continue

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = json.load(f)

            text = page.get_text()

            # Verify that the text in the JSON matches the text in the PDF
            if "request" in content and "text" in content["request"] and content["request"]["text"] != text:
                print(f"Warning: Text in JSON file does not match text in PDF for page {count}.")
                if verbose:
                    print("This may cause incorrect redaction placement.")

            if "response" in content:
                results = content["response"]
                process_presidio_results(results=results, page=page, text=text, should_redact=should_redact, verbose=verbose)
            else:
                print(f"Warning: No response data found in JSON file for page {count}.")

        except (json.JSONDecodeError, OSError) as e:
            print(f"Error reading JSON file for page {count}: {e}")

        count += 1

def save_pdf(pdf, output_dir, has_been_highlighted=False):
    """
    Save the redacted PDF to the output directory with a modified name.

    Args:
        pdf (fitz.Document): The PyMuPDF document object to save.
        output_dir (Path): The output directory path where the file will be saved.
        has_been_highlighted (bool): Sets prefix to HIGHLIGHTED_ if set to True. Defaults to False.
    """
    prefix = "REDACTED_" if not has_been_highlighted else "HIGHLIGHTED_"
    pdf_name = prefix + Path(pdf.name).name
    output_path = output_dir / pdf_name

    try:
        pdf.save(str(output_path))
        print(f"[SUCCESS] Saved redacted PDF to {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save PDF: {e}")

def save_logs_for_pdf(pdf, output_dir, log_dict):
    folder_name = Path(pdf.name).stem + "_LOGS"
    output_path = output_dir / folder_name
    output_path.mkdir(parents=True, exist_ok=True)

    for page in log_dict:
        file_name = f"page_{page['page']}.json"
        content = {
            "request": page["request"],
            "response": page["response"]
        }

        try:
            with open(output_path / file_name, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
        except (OSError, TypeError, ValueError) as e:
            print(f"Failed to write log for page {page['page']}: {e}")


def process_document_list(document_list, output_dir, log_to_json=False, should_redact=True, json_input_dir=None):
    """
    Process a list of PDFs, redacting sensitive content and saving results.

    Args:
        document_list (List[fitz.Document]): A list of PyMuPDF PDF document objects.
        output_dir (Path): The output directory where redacted files will be stored.
        log_to_json (bool): If True, save Presidio input/output logs. Defaults to False.
        should_redact (bool): If True, redact. If False, highlight. Defaults to True.
        json_input_dir (Path): Path to directory containing JSON files with redaction information. If provided,
                              uses these files instead of calling Presidio API. Defaults to None.
    """

    for pdf in document_list:
        if json_input_dir:
            # Use JSON input instead of Presidio API
            pdf_name = Path(pdf.name).stem
            # TODO: If f is set, do as it is now, if d is set (Input flags for guard), give the directory for all log folders.
            pdf_json_dir = json_input_dir # / f"{pdf_name}_LOGS"
            expected_dir_name = f"{pdf_name}_LOGS"

            if not json_input_dir.name == expected_dir_name:
                print("Warning: The given directory name does not match exactly our format of <pdf-file-name>_LOGS. If you the output is incorrect, check if you have given the correct folder.")
            
            if not pdf_json_dir.exists() or not pdf_json_dir.is_dir():
                print(f"Warning: JSON directory {pdf_json_dir} not found for {pdf_name}. Skipping this PDF.")
                continue

            process_pdf_with_json(pdf=pdf, json_dir=pdf_json_dir, should_redact=should_redact)
            save_pdf(pdf=pdf, output_dir=output_dir, has_been_highlighted=(not should_redact))
        else:
            # Use Presidio API
            log_dict = process_pdf(pdf=pdf, generate_log=log_to_json, should_redact=should_redact)
            save_pdf(pdf=pdf, output_dir=output_dir, has_been_highlighted=(not should_redact))
            if log_to_json:
                save_logs_for_pdf(pdf=pdf, output_dir=output_dir, log_dict=log_dict)


def is_supported_language(lang_code: str) -> bool:
    """Return True if the language code is supported internally."""
    return lang_code in LANGUAGES_DISPLAY


def format_supported_languages() -> str:
    """Return a nicely formatted string of supported languages for user display."""
    return ",\n ".join(f"{name} ({code})" for code, name in LANGUAGES_DISPLAY.items())

def main(args):

    document_list = []

    used_language = args.language or DEFAULT_LANGUAGE

    log_results_into_json = args.json_log or args.highlight
    highlight_mode = args.highlight
    json_input_dir = args.json_input

    if args.output:
        output_dir = args.output
    else:
        output_dir = Path("./redacted") if not highlight_mode else Path("./highlighted_redaction")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Only check language if we're not using JSON input (since language is only used for Presidio API)
    if not json_input_dir and not is_supported_language(used_language):
        print(f"'{used_language}' is not supported. We currently support: \n {format_supported_languages()}")
        sys.exit(1)

    if args.file:
        if not args.file.is_file():
            print(f"Error: {args.file} is not a valid file.")
            sys.exit(1)
        if args.file.suffix.lower() != ".pdf":
            print(f"Error: {args.file} is not a PDF file.")
            sys.exit(1)
        else:
            print(f"Processing file: {args.file}")
            file_handler = FileHandler(args.file, "file")
            document = file_handler.get_document_list()
            document_list.extend(document)

    if args.directory:
        if not args.directory.is_dir():
            print(f"Error: {args.directory} is not a valid directory.")
            sys.exit(1)
        else:
            print(f"Processing directory: {args.directory}")
            file_handler = FileHandler(args.directory, "dir")
            documents = file_handler.get_document_list()
            document_list.extend(documents)

    if not args.file and not args.directory:
        print("Error: You must provide either a file (-f) or a directory (-d).")
        sys.exit(1)

    if json_input_dir:
        if not json_input_dir.is_dir():
            print(f"Error: {json_input_dir} is not a valid directory.")
            sys.exit(1)
        print(f"Using JSON input from: {json_input_dir}")

    process_document_list(
        document_list=document_list,
        output_dir=output_dir,
        log_to_json=log_results_into_json,
        should_redact=(not highlight_mode),
        json_input_dir=json_input_dir
    )

    print(f"Documents parsed to text: {len(document_list)}")
    print(f"Redacted files saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and redact PDF files.")
    parser.add_argument("-i", "--json-input", type=Path, help="Path to a directory containing a directory containing JSON files with redaction information. (for example '-i redacted -f filename.pdf' for json files in 'redacted/<filename>_LOGS/page_0.json' and a file at 'filename.pdf')")
    parser.add_argument("-f", "--file", type=Path, help="Path to a PDF file")
    parser.add_argument("-d", "--directory", type=Path,
                        help="Path to a directory containing one or multiple PDF files to redact.")
    parser.add_argument("-o", "--output", type=Path,
                        help="Directory where the redacted files will be saved. Defaults to './redacted'.")
    parser.add_argument("-l", "--language", type=str,
                        help=f"Language for Presidio analysis. We currently support: {format_supported_languages()}\n Defaults to 'de'.")
    parser.add_argument("-j", "--json-log", action="store_true",
                        help="Enable JSON logging. Saves Presidio input/output logs per page in the specified output folder.")
    parser.add_argument("--highlight", action="store_true",
                        help="Disables redaction of documents, and highlights the detected sections instead redacting them.")

    # We only need to parse the json-input argument here, the full parsing happens in main()
    args, _ = parser.parse_known_args()

    # Only check API availability if we're not using JSON input
    if not args.json_input:
        check_api_available(presidio_api_endpoint)

    main(args)
