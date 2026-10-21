"""
Analysis Routes Blueprint.
Handles health checks, resume-job matching analysis, and SQLite history management.
"""
import sys
import os

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from flask import Blueprint, request, jsonify

try:
    from config import Config
    from services.resume_analyzer import ResumeAnalyzer
    from utils.validators import validate_analysis_input, ValidationError
    from database import save_analysis, get_history, get_analysis_by_id, delete_analysis, clear_history
except ImportError:
    from backend.config import Config
    from backend.services.resume_analyzer import ResumeAnalyzer
    from backend.utils.validators import validate_analysis_input, ValidationError
    from backend.database import save_analysis, get_history, get_analysis_by_id, delete_analysis, clear_history

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api")

@analysis_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint and backend configuration status."""
    ai_active = Config.is_ai_configured()
    return jsonify({
        "status": "healthy",
        "service": "AI Resume Analyzer Backend",
        "ai_configured": ai_active,
        "ai_model": Config.GEMINI_MODEL if ai_active else "None (Transparent Rule Engine Demo Active)",
        "features": {
            "pdf_support": True,
            "docx_support": True,
            "pdf_report_generation": True,
            "history_storage": True
        }
    }), 200

@analysis_bp.route("/analyze", methods=["POST"])
def analyze_resume():
    """
    Analyze resume against target job description.
    Expects JSON: { resume_text, job_description, job_title, force_demo }
    """
    try:
        raw_data = request.get_json(silent=True)
        validated = validate_analysis_input(raw_data)
        
        result = ResumeAnalyzer.analyze(
            resume_text=validated["resume_text"],
            job_description=validated["job_description"],
            job_title=validated["job_title"],
            force_demo=validated["force_demo"]
        )
        
        mode_used = result.get("analysis_mode", "Rule Engine")
        analysis_id = save_analysis(
            job_title=validated["job_title"],
            result=result,
            mode=mode_used
        )
        result["analysis_id"] = analysis_id
        
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@analysis_bp.route("/history", methods=["GET"])
def fetch_history():
    """Retrieve list of past analysis records."""
    try:
        records = get_history(limit=30)
        return jsonify({"history": records}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve history: {str(e)}"}), 500

@analysis_bp.route("/history/<int:analysis_id>", methods=["GET"])
def fetch_analysis_detail(analysis_id):
    """Retrieve full detail for a single analysis record."""
    record = get_analysis_by_id(analysis_id)
    if not record:
        return jsonify({"error": f"Analysis record #{analysis_id} not found."}), 404
    return jsonify(record), 200

@analysis_bp.route("/history/<int:analysis_id>", methods=["DELETE"])
def remove_history_item(analysis_id):
    """Delete a single analysis record."""
    success = delete_analysis(analysis_id)
    if not success:
        return jsonify({"error": f"Record #{analysis_id} not found or already deleted."}), 404
    return jsonify({"message": f"Analysis #{analysis_id} deleted successfully."}), 200

@analysis_bp.route("/history", methods=["DELETE"])
def clear_all_history():
    """Clear all analysis records from history."""
    count = clear_history()
    return jsonify({"message": f"Successfully deleted {count} history records."}), 200
