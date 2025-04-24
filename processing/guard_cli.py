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

#check if presidio is available
response = requests.get(presidio_api_endpoint + "/health")
if response.status_code != 200:
    print(f"Presidio service not available!")
    sys.exit(1)

def process_presidio_results(results, page, text):
    for entity in results:
        matched_text = text[entity["start"]:entity["end"]]
        for area in page.search_for(matched_text):
            page.add_redact_annot(area, fill=(0, 0, 0))

    page.apply_redactions()

def process_pdf(pdf):
    pdf_name = Path(pdf.name).name
    print("Processing:" + pdf_name)
    for page in pdf:
        text = page.get_text()
        built_request = {
            "text": text,
            "language": "de"
        }
        response = requests.post(presidio_api_analysis, json=built_request)
        if response.status_code != 200:
            print(f"Presidio error for: {pdf_name} ")
            print(response.text)
            continue

        results = response.json()
        process_presidio_results(results=results, page=page, text=text)

def safe_pdf(pdf, output_dir):
    pdf_name = "REDACTED_" + Path(pdf.name).name
    output_path = output_dir / pdf_name
    pdf.save(str(output_path))
    

def process_document_list(document_list, output_dir):
    for pdf in document_list:
        success = process_pdf(pdf=pdf)
        if(success): 
            safe_pdf(pdf=pdf, output_dir=output_dir)

def main():
    parser = argparse.ArgumentParser(description="Process and redact PDF files.")
    parser.add_argument("-f", "--file", type=Path, help="Path to a PDF file")
    parser.add_argument("-d", "--directory", type=Path, help="Path to a directory")
    parser.add_argument("-o", "--output", type=Path, help="Output directory for redacted files")
    args = parser.parse_args()
    
    output_dir = args.output if args.output else Path("./redacted")
    output_dir.mkdir(exist_ok=True)

    document_list = []
    
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