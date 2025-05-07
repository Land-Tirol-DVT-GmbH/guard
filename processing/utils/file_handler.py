import fitz
from pathlib import Path

class FileHandler:
    def __init__(self, path, type):
        self.path = Path(path)
        self.type = type
    
    def read_pdf_to_document(self, pdf_file):
        """Read PDF as a document."""
        print(f"\nReading: {pdf_file}")
        document = fitz.open(pdf_file)
        return document
        # return "\n".join([page.get_text() for page in document])
    
    def get_document_list(self):
        """
        Read file(s) and return text content.
        returns document_list: An array consisting of fitz.document objects, representing each pdf read.
        """
        document_list = []
        if self.type == "file":
            doc = self.read_pdf_to_document(str(self.path))
            document_list.append(doc)

        elif self.type == "dir":
            pdf_list = list(self.path.glob("*.pdf"))
            if not pdf_list:
                print(f"No PDF files found in {self.path}")
                return document_list
            print(f"Processing {len(pdf_list)} PDF files in {self.path}")
            for pdf_file in pdf_list:
                doc = self.read_pdf_to_document(str(pdf_file))
                document_list.append(doc)
        return document_list