# CLI entry point for using guard pdf redaction.

import sys
import argparse
from pathlib import Path
# ToDo: move helper_classes to utils
from utils.file_handler import FileHandler 

def noImplementation():
    print("No implementation")

def main():
    parser = argparse.ArgumentParser(description="Process and redact PDF files.")
    parser.add_argument("-f", "--file", type=Path, help="Path to a PDF file")
    parser.add_argument("-d", "--directory", type=Path, help="Path to a directory")
    parser.add_argument("-o", "--output", type=Path, help="Output directory for redacted files")
    args = parser.parse_args()
    
    output_dir = args.output if args.output else Path("./redacted")
    output_dir.mkdir(exist_ok=True)
    
    # redactor = Redactor()
    
    # each document is read in as a string, for a single file, only one document is added 
    # to document_list, for a directory, each pdf is added as a string.
    document_list = []
    processed_files = []
    
    if args.file:
        if not args.file.is_file():
            print(f"Error: {args.file} is not a valid file.")
            sys.exit(1)
        if args.file.suffix.lower() != ".pdf":
            print(f"Error: {args.file} is not a PDF file.")
            sys.exit(1)
        else:
            print(f"Processing file: {args.file}")
            # noImplementation()
            file_handler = FileHandler(args.file, "file")
            document = file_handler.get_document_list()
            document_list.extend(document)
            print(document)
            output_path = output_dir / f"redacted_{args.file.name}"
            # redactor.redact_document(document, str(args.file), str(output_path))
            # processed_files.append(output_path)

    if args.directory:
        if not args.directory.is_dir():
            print(f"Error: {args.directory} is not a valid directory.")
            sys.exit(1)
        else:
            print(f"Processing directory: {args.directory}")
            noImplementation()
            file_handler = FileHandler(args.directory, "dir")
            documents = file_handler.get_document_list()
            document_list.extend(documents)
            # pdf_files = list(args.directory.glob("*.pdf"))
            # for doc, pdf_file in zip(documents, pdf_files):
            #     output_path = output_dir / f"redacted_{pdf_file.name}"
            #     redactor.redact_document(doc, str(pdf_file), str(output_path))
            #     processed_files.append(output_path)

    if not args.file and not args.directory:
        print("Error: You must provide either a file (-f) or a directory (-d).")
        sys.exit(1)
    
    print(f"Documents parsed to text: {len(document_list)}")
    print(f"Documents redacted: {len(processed_files)}")
    print(f"Redacted files saved to: {output_dir}")

if __name__ == "__main__":
    main()