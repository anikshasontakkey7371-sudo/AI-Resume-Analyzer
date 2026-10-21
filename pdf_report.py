"""
PDF Report Generator Module (Backwards Compatibility Module).
Delegates core functionality to services.report_generator.
"""
import sys
import os

_BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

try:
    from services.report_generator import ReportGenerator
except ImportError:
    from backend.services.report_generator import ReportGenerator

def generate_pdf_report(analysis_data: dict):
    return ReportGenerator.generate_pdf(analysis_data)
