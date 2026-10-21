"""
AI Resume Analyzer Backend Package.
"""
import sys
import os

# Ensure backend root is in Python sys.path
_BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
