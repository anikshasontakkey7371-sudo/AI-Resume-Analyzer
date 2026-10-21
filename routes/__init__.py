"""
Routes package for AI Resume Analyzer backend.
Registers blueprints with the Flask application.
"""
from flask import Flask
from .resume_routes import resume_bp
from .analysis_routes import analysis_bp
from .report_routes import report_bp

def register_routes(app: Flask):
    """Register all application blueprints."""
    app.register_blueprint(resume_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(report_bp)

__all__ = [
    "register_routes",
    "resume_bp",
    "analysis_bp",
    "report_bp"
]
