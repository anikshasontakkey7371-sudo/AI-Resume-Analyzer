"""
Configuration management for AI Resume Analyzer backend.
Centralizes environment variables and application constants.
"""
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class Config:
    """Base application configuration."""
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development").lower() == "development"
    
    # AI Engine Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # File Upload Limits & Extensions
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'.pdf', '.docx'}
    
    # SQLite Database Path
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "resume_history.db")
    
    # Score Weighting Formula
    WEIGHT_SKILLS = 0.40
    WEIGHT_EXPERIENCE = 0.25
    WEIGHT_KEYWORDS = 0.20
    WEIGHT_FORMATTING = 0.15

    @classmethod
    def is_ai_configured(cls) -> bool:
        """Check if a valid Gemini API key is configured."""
        return bool(cls.GEMINI_API_KEY and len(cls.GEMINI_API_KEY) > 10)
