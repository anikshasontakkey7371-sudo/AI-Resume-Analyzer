"""
Resume Routes Blueprint.
Handles file uploads, text extraction, and sample testing datasets.
"""
import sys
import os

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from flask import Blueprint, request, jsonify

try:
    from services.resume_parser import ResumeParser, ParsingError
    from utils.validators import FileValidationError
    from sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS
except ImportError:
    from backend.services.resume_parser import ResumeParser, ParsingError
    from backend.utils.validators import FileValidationError
    from backend.sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS

resume_bp = Blueprint("resume", __name__, url_prefix="/api")

@resume_bp.route("/extract-text", methods=["POST"])
def extract_text():
    """Extract readable text from uploaded PDF or DOCX resume."""
    if "file" not in request.files:
        return jsonify({"error": "No file included in the upload request."}), 400
        
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400
        
    try:
        result = ResumeParser.extract_from_storage(file)
        return jsonify(result), 200
    except FileValidationError as e:
        return jsonify({"error": str(e)}), 422
    except ParsingError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Failed to extract document text: {str(e)}"}), 500

@resume_bp.route("/sample-data", methods=["GET"])
def get_sample_data():
    """Returns sample resumes and job requisitions for 1-click demos."""
    return jsonify({
        "resumes": SAMPLE_RESUMES,
        "job_descriptions": SAMPLE_JOB_DESCRIPTIONS
    }), 200
