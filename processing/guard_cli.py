import os
import sys
import argparse
from pathlib import Path
import requests
from utils.file_handler import FileHandler 
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

presidio_api_endpoint = os.environ.get("PRESIDIO_API_ENDPOINT")
presidio_api_analysis = presidio_api_endpoint + "/analyze"

used_language = "de"

LANGUAGES_DISPLAY = {
    "de": "German",
    "en": "English",
    "it": "Italian"
}

#TODO: Verbose mode maybe?


#check if presidio is available
response = requests.get(presidio_api_endpoint + "/health")
if response.status_code != 200:
    print(f"Presidio service not available!")
    sys.exit(1)

def process_presidio_results(results, page, text):
    """
    Apply redaction annotations to a PDF page based on Presidio analysis results.

    Args:
        results (List[Dict]): List of recognized PII entities, each with 'start' and 'end' offsets.
        page (fitz.Page): The PDF page object from PyMuPDF to apply redactions on.
        text (str): Full text content of the page, used to locate entities.
    """
    for entity in results:
        matched_text = text[entity["start"]:entity["end"]]
        for area in page.search_for(matched_text):
            page.add_redact_annot(area, fill=(0, 0, 0))

    page.apply_redactions()


def process_pdf(pdf):
    """
    Analyze and redact sensitive information in a single PDF using Presidio.

    Args:
        pdf (fitz.Document): A PyMuPDF document object representing the input PDF.
    """
    pdf_name = Path(pdf.name).name
    print("Processing:" + pdf_name)
    for page in pdf:
        text = page.get_text()
        built_request = {
            "text": text,
            "language": used_language
        }
        response = requests.post(presidio_api_analysis, json=built_request)
        if response.status_code != 200:
            print(f"Presidio error for: {pdf_name} ")
            print(response.text)
            continue

        results = response.json()
        process_presidio_results(results=results, page=page, text=text)

def save_pdf(pdf, output_dir):
    """
    Save the redacted PDF to the output directory with a modified name.

    Args:
        pdf (fitz.Document): The PyMuPDF document object to save.
        output_dir (Path): The output directory path where the file will be saved.
    """
    pdf_name = "REDACTED_" + Path(pdf.name).name
    output_path = output_dir / pdf_name

    try:
        pdf.save(str(output_path))
        print(f"[SUCCESS] Saved redacted PDF to {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save PDF: {e}")
    

def process_document_list(document_list, output_dir):
    """
    Process a list of PDFs, redacting sensitive content and saving results.

    Args:
        document_list (List[fitz.Document]): A list of PyMuPDF PDF document objects.
        output_dir (Path): The output directory where redacted files will be stored.
    """

    for pdf in document_list:
        process_pdf(pdf=pdf)
        save_pdf(pdf=pdf, output_dir=output_dir)


def is_supported_language(lang_code: str) -> bool:
    """Return True if the language code is supported internally."""
    return lang_code in LANGUAGES_DISPLAY


def format_supported_languages() -> str:
    """Return a nicely formatted string of supported languages for user display."""
    return ",\n ".join(f"{name} ({code})" for code, name in LANGUAGES_DISPLAY.items())

def main():
    parser = argparse.ArgumentParser(description="Process and redact PDF files.")
    parser.add_argument("-f", "--file", type=Path, help="Path to a PDF file")
    parser.add_argument("-d", "--directory", type=Path, help="Path to a directory containing one or multiple PDF files to redact.")
    parser.add_argument("-o", "--output", type=Path, help="Directory where the redacted files will be saved. Defaults to './redacted'.")
    parser.add_argument("-l", "--language", type=str, help=f"Language for Presidio analysis. We currently support: {format_supported_languages()}\n Defaults to 'de'.")
    args = parser.parse_args()

    document_list = []

    if args.output:
        output_dir = args.output
    else:
        output_dir = Path("./redacted")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not is_supported_language(args.language):
        print(f"'{args.language}' is not supported. We currently support: \n {format_supported_languages()}")
        sys.exit(1)

    used_language = args.language

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

    process_document_list(document_list=document_list, output_dir=output_dir)
    
    print(f"Documents parsed to text: {len(document_list)}")
    print(f"Redacted files saved to: {output_dir}")

if __name__ == "__main__":
    main()