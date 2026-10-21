"""
Resume text extraction and validation utility (Backwards Compatibility Module).
Delegates core functionality to services.resume_parser and utils.validators.
"""
import sys
import os

_BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

try:
    from services.resume_parser import ResumeParser, ParsingError
    from utils.validators import validate_file, FileValidationError
except ImportError:
    from backend.services.resume_parser import ResumeParser, ParsingError
    from backend.utils.validators import validate_file, FileValidationError

# Backward compatibility alias
ExtractionError = ParsingError

def extract_text_from_pdf(file_stream) -> str:
    return ResumeParser.extract_from_pdf(file_stream)

def extract_text_from_docx(file_stream) -> str:
    return ResumeParser.extract_from_docx(file_stream)

def extract_text(file_storage) -> dict:
    return ResumeParser.extract_from_storage(file_storage)

if __name__ == "__main__":
    print("Testing extractor.py (modular alias)...")
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data")
    pdf_test = os.path.join(sample_dir, "sample_resume.pdf")
    docx_test = os.path.join(sample_dir, "sample_resume.docx")
    
    if os.path.exists(pdf_test):
        with open(pdf_test, "rb") as f:
            pdf_res = extract_text_from_pdf(f)
            print(f"  [PDF OK] Extracted {len(pdf_res.split())} words.")
            
    if os.path.exists(docx_test):
        with open(docx_test, "rb") as f:
            docx_res = extract_text_from_docx(f)
            print(f"  [DOCX OK] Extracted {len(docx_res.split())} words.")
    print("Extractor alias verification completed successfully.")
