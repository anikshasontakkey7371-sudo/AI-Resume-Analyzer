"""
Comprehensive Unit and Integration Tests for AI Resume Analyzer Backend.
"""
import os
import io
import pytest
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from extractor import validate_file, extract_text_from_pdf, extract_text_from_docx, ExtractionError
from analyzer import analyze_resume, extract_skills_from_text, clean_text
from database import init_db, save_analysis, get_history, delete_analysis, clear_history
from pdf_report import generate_pdf_report
from sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_validate_file():
    # Valid files
    is_valid, msg = validate_file("resume.pdf", 1024)
    assert is_valid is True
    assert msg == ""

    is_valid, msg = validate_file("resume.docx", 2048)
    assert is_valid is True

    # Invalid extension
    is_valid, msg = validate_file("resume.exe", 1024)
    assert is_valid is False
    assert "Unsupported file type" in msg

    # Oversized file (> 5MB)
    is_valid, msg = validate_file("resume.pdf", 6 * 1024 * 1024)
    assert is_valid is False
    assert "exceeds maximum limit" in msg

def test_extract_sample_files():
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sample_data"))
    pdf_path = os.path.join(sample_dir, "sample_resume.pdf")
    docx_path = os.path.join(sample_dir, "sample_resume.docx")

    assert os.path.exists(pdf_path), "sample_resume.pdf should exist"
    assert os.path.exists(docx_path), "sample_resume.docx should exist"

    # Test PDF extraction
    with open(pdf_path, "rb") as f:
        pdf_text = extract_text_from_pdf(f)
        assert len(pdf_text) > 100
        assert "Alex Morgan" in pdf_text or "Python" in pdf_text

    # Test DOCX extraction
    with open(docx_path, "rb") as f:
        docx_text = extract_text_from_docx(f)
        assert len(docx_text) > 100
        assert "Samantha Chen" in docx_text or "Python" in docx_text

def test_rule_based_analyzer():
    resume_text = SAMPLE_RESUMES["software_engineer"]["text"]
    job_desc = SAMPLE_JOB_DESCRIPTIONS["software_engineer"]["text"]

    result = analyze_resume(resume_text, job_desc, job_title="Senior Full Stack Engineer", force_demo=True)

    assert result["is_ai_powered"] is False
    assert "scores" in result
    scores = result["scores"]
    assert 0 <= scores["overall"] <= 100
    assert 0 <= scores["skills_match"] <= 100
    assert 0 <= scores["experience_relevance"] <= 100
    assert 0 <= scores["keyword_coverage"] <= 100
    assert 0 <= scores["formatting_readability"] <= 100

    assert len(result["skills_matched"]) > 0
    assert "strengths" in result
    assert "improvements" in result
    assert "bullet_point_suggestions" in result
    assert "recommended_skills_to_learn" in result
    assert "transparent_criteria" in result

def test_flask_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "ai_configured" in data

def test_flask_sample_data_endpoint(client):
    res = client.get("/api/sample-data")
    assert res.status_code == 200
    data = res.get_json()
    assert "resumes" in data
    assert "job_descriptions" in data

def test_flask_extract_endpoint_success(client):
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sample_data"))
    pdf_path = os.path.join(sample_dir, "sample_resume.pdf")

    with open(pdf_path, "rb") as f:
        data = {
            "file": (io.BytesIO(f.read()), "sample_resume.pdf")
        }
        res = client.post("/api/extract-text", data=data, content_type="multipart/form-data")
        assert res.status_code == 200
        res_data = res.get_json()
        assert res_data["extension"] == ".pdf"
        assert res_data["word_count"] > 50

def test_flask_extract_endpoint_invalid_file(client):
    data = {
        "file": (io.BytesIO(b"fake binary"), "malicious.exe")
    }
    res = client.post("/api/extract-text", data=data, content_type="multipart/form-data")
    assert res.status_code == 422
    assert "Unsupported file type" in res.get_json()["error"]

def test_flask_analyze_endpoint(client):
    payload = {
        "resume_text": SAMPLE_RESUMES["software_engineer"]["text"],
        "job_description": SAMPLE_JOB_DESCRIPTIONS["software_engineer"]["text"],
        "job_title": "Full Stack Dev",
        "force_demo": True
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "scores" in data
    assert "analysis_id" in data

def test_flask_history_flow(client):
    # Get initial history
    res = client.get("/api/history")
    assert res.status_code == 200
    data = res.get_json()
    assert "history" in data

    # Clear history
    res = client.delete("/api/history")
    assert res.status_code == 200

    # Run an analysis to insert one
    payload = {
        "resume_text": SAMPLE_RESUMES["software_engineer"]["text"],
        "job_description": SAMPLE_JOB_DESCRIPTIONS["software_engineer"]["text"],
        "job_title": "Test Engineer",
        "force_demo": True
    }
    analyze_res = client.post("/api/analyze", json=payload)
    item_id = analyze_res.get_json()["analysis_id"]

    # Verify present in history
    hist_res = client.get("/api/history")
    items = hist_res.get_json()["history"]
    assert any(h["id"] == item_id for h in items)

    # Get single item
    item_res = client.get(f"/api/history/{item_id}")
    assert item_res.status_code == 200
    assert item_res.get_json()["job_title"] == "Test Engineer"

    # Delete single item
    del_res = client.delete(f"/api/history/{item_id}")
    assert del_res.status_code == 200

def test_generate_pdf_report(client):
    resume_text = SAMPLE_RESUMES["software_engineer"]["text"]
    job_desc = SAMPLE_JOB_DESCRIPTIONS["software_engineer"]["text"]
    result = analyze_resume(resume_text, job_desc, job_title="Senior Dev", force_demo=True)

    pdf_buffer = generate_pdf_report(result)
    pdf_bytes = pdf_buffer.getvalue()
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

    # Test via API
    res = client.post("/api/generate-pdf", json={"analysis_data": result})
    assert res.status_code == 200
    assert res.headers["Content-Type"] == "application/pdf"
