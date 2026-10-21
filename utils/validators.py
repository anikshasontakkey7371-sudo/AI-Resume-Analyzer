"""
Validation utilities for AI Resume Analyzer.
"""
import os
import sys
from typing import Optional, Tuple, Dict, Any

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

try:
    from config import Config
except ImportError:
    from backend.config import Config

class ValidationError(Exception):
    """Raised when request payload or parameters fail validation."""
    pass

class FileValidationError(ValidationError):
    """Raised when an uploaded file fails type or size validation."""
    pass

def validate_file(filename: str, file_size: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validate file extension and size against configured limits.
    Returns (is_valid, error_message).
    """
    if not filename:
        return False, "No file provided."
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in Config.ALLOWED_EXTENSIONS:
        allowed = ", ".join(Config.ALLOWED_EXTENSIONS)
        return False, f"Unsupported file type '{ext}'. Allowed formats are: {allowed}."
    
    if file_size is not None and file_size > Config.MAX_FILE_SIZE_BYTES:
        mb_size = round(file_size / (1024 * 1024), 2)
        max_mb = round(Config.MAX_FILE_SIZE_BYTES / (1024 * 1024), 1)
        return False, f"File size ({mb_size}MB) exceeds maximum limit of {max_mb}MB."
        
    return True, ""

def validate_analysis_input(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate analysis request JSON payload.
    Ensures both resume_text and job_description are provided and meet minimum length.
    """
    if not data or not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")
        
    resume_text = (data.get("resume_text") or "").strip()
    job_description = (data.get("job_description") or "").strip()
    job_title = (data.get("job_title") or "").strip()
    force_demo = bool(data.get("force_demo", False))
    
    if not resume_text:
        raise ValidationError("Resume text is required. Please upload a resume file or paste resume content.")
        
    if not job_description:
        raise ValidationError("Job description is required. Please paste the target job requirements.")
        
    if len(resume_text) < 40:
        raise ValidationError(f"Resume text is too short ({len(resume_text)} chars). Please provide at least 40 characters.")
        
    if len(job_description) < 40:
        raise ValidationError(f"Job description is too short ({len(job_description)} chars). Please provide at least 40 characters.")
        
    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "job_title": job_title,
        "force_demo": force_demo
    }

def validate_pdf_request(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate PDF generation payload."""
    if not data or not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")
        
    if not data.get("analysis_data") and not data.get("analysis_id"):
        raise ValidationError("Either 'analysis_data' or 'analysis_id' must be provided to generate a PDF report.")
        
    return data
