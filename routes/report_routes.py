"""
Report Routes Blueprint.
Handles generating and streaming branded PDF evaluation reports.
"""
import sys
import os

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from flask import Blueprint, request, jsonify, send_file

try:
    from services.report_generator import ReportGenerator
    from utils.validators import validate_pdf_request, ValidationError
    from database import get_analysis_by_id
except ImportError:
    from backend.services.report_generator import ReportGenerator
    from backend.utils.validators import validate_pdf_request, ValidationError
    from backend.database import get_analysis_by_id

report_bp = Blueprint("report", __name__, url_prefix="/api")

@report_bp.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    """Generate and stream a downloadable PDF evaluation report."""
    try:
        raw_data = request.get_json(silent=True)
        validated = validate_pdf_request(raw_data)
        
        analysis_data = validated.get("analysis_data")
        if not analysis_data and "analysis_id" in validated:
            record = get_analysis_by_id(validated["analysis_id"])
            if record and "result" in record:
                analysis_data = record["result"]
                
        if not analysis_data:
            return jsonify({"error": "Valid analysis data could not be resolved."}), 400
            
        pdf_buffer = ReportGenerator.generate_pdf(analysis_data)
        role = (analysis_data.get("target_role") or "Job").replace(" ", "_")
        filename = f"Resume_Analysis_Report_{role}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF report: {str(e)}"}), 500
