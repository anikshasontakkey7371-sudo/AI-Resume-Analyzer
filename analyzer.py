"""
Resume Analyzer Module (Backwards Compatibility Module).
Delegates core functionality to services.resume_analyzer.
"""
import sys
import os
from typing import Optional

_BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

try:
    from services.resume_analyzer import ResumeAnalyzer
except ImportError:
    from backend.services.resume_analyzer import ResumeAnalyzer

def analyze_resume(resume_text: str, job_description: str, job_title: Optional[str] = None, force_demo: bool = False) -> dict:
    return ResumeAnalyzer.analyze(
        resume_text=resume_text,
        job_description=job_description,
        job_title=job_title,
        force_demo=force_demo
    )

def extract_skills_from_text(text: str) -> set:
    return ResumeAnalyzer.extract_skills(text)

def clean_text(text: str) -> str:
    return ResumeAnalyzer.clean_text(text)
