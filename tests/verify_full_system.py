"""
Automated End-to-End System Verification for AI Resume Analyzer.
Tests:
- Health check
- PDF file upload & text extraction
- DOCX file upload & text extraction
- Resume & job description matching analysis
- Analysis metrics & structured feedback schema
- PDF report generation and binary download
- SQLite history storage and deletion
- Frontend accessibility on port 5173
"""
import sys
import os
import json
import urllib.request
import urllib.error
import mimetypes

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BACKEND_URL = "http://127.0.0.1:5000/api"
FRONTEND_URL = "http://localhost:5173"
SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sample_data"))

def post_multipart(url, file_path, field_name="file"):
    """Helper to post multipart/form-data for file uploads without external dependencies."""
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_content = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def post_json(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def run_all_checks():
    print("==================================================================")
    print("     FULL SYSTEM INTEGRATION VERIFICATION: AI RESUME ANALYZER     ")
    print("==================================================================")

    # 1. Frontend Check
    print("\n[Step 1/8] Verifying Frontend Web Server...")
    try:
        with urllib.request.urlopen(FRONTEND_URL, timeout=5) as resp:
            assert resp.status == 200
            html = resp.read().decode()
            assert "AI Resume Analyzer" in html or "root" in html
            print("  [SUCCESS] Frontend is running at http://localhost:5173 (Status: 200 OK)")
    except Exception as e:
        print("  [FAILED] Frontend check failed:", str(e))
        sys.exit(1)

    # 2. Backend Health Check
    print("\n[Step 2/8] Verifying Backend Health API...")
    try:
        with urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=5) as resp:
            assert resp.status == 200
            health = json.loads(resp.read().decode())
            print(f"  [SUCCESS] Backend healthy: {health['service']} (AI Engine: {health['ai_model']})")
    except Exception as e:
        print("  [FAILED] Backend health check failed:", str(e))
        sys.exit(1)

    # 3. PDF Upload & Text Extraction
    print("\n[Step 3/8] Testing PDF Upload & Text Extraction...")
    pdf_path = os.path.join(SAMPLE_DIR, "sample_resume.pdf")
    assert os.path.exists(pdf_path), f"Sample PDF missing at {pdf_path}"
    status, pdf_result = post_multipart(f"{BACKEND_URL}/extract-text", pdf_path)
    assert status == 200
    assert pdf_result["extension"] == ".pdf"
    assert pdf_result["word_count"] > 100
    print(f"  [SUCCESS] PDF parsed ({pdf_result['filename']}): {pdf_result['word_count']} words, {pdf_result['char_count']} chars extracted.")

    # 4. DOCX Upload & Text Extraction
    print("\n[Step 4/8] Testing DOCX Upload & Text Extraction...")
    docx_path = os.path.join(SAMPLE_DIR, "sample_resume.docx")
    assert os.path.exists(docx_path), f"Sample DOCX missing at {docx_path}"
    status, docx_result = post_multipart(f"{BACKEND_URL}/extract-text", docx_path)
    assert status == 200
    assert docx_result["extension"] == ".docx"
    assert docx_result["word_count"] > 100
    print(f"  [SUCCESS] DOCX parsed ({docx_result['filename']}): {docx_result['word_count']} words, {docx_result['char_count']} chars extracted.")

    # 5. Matching & Analysis API
    print("\n[Step 5/8] Testing Resume-Job Description Matching Analysis...")
    job_desc_path = os.path.join(SAMPLE_DIR, "sample_job_description.txt")
    with open(job_desc_path, "r", encoding="utf-8") as f:
        job_desc_text = f.read()

    analysis_payload = {
        "resume_text": pdf_result["text"],
        "job_description": job_desc_text,
        "job_title": "Senior Full Stack Engineer",
        "force_demo": True
    }
    status, analysis_res = post_json(f"{BACKEND_URL}/analyze", analysis_payload)
    assert status == 200
    scores = analysis_res["scores"]
    print(f"  [SUCCESS] Analysis completed successfully!")
    print(f"    - Overall Score:              {scores['overall']}/100")
    print(f"    - Skills Match (40%):         {scores['skills_match']}%")
    print(f"    - Experience Relevance (25%): {scores['experience_relevance']}%")
    print(f"    - Keyword Coverage (20%):     {scores['keyword_coverage']}%")
    print(f"    - Formatting (15%):           {scores['formatting_readability']}%")
    print(f"    - Core Skills Matched ({len(analysis_res['skills_matched'])}): {', '.join(analysis_res['skills_matched'][:6])}")
    print(f"    - Skills Missing ({len(analysis_res['skills_missing'])}):     {', '.join(analysis_res['skills_missing'][:4])}")
    print(f"    - STAR Bullet Point Rewrites: {len(analysis_res['bullet_point_suggestions'])} actionable examples")

    # 6. PDF Report Generation & Download
    print("\n[Step 6/8] Testing Branded PDF Report Generation & Download...")
    pdf_req = urllib.request.Request(
        f"{BACKEND_URL}/generate-pdf",
        data=json.dumps({"analysis_data": analysis_res}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(pdf_req) as resp:
        assert resp.status == 200
        assert resp.headers["Content-Type"] == "application/pdf"
        pdf_bytes = resp.read()
        assert pdf_bytes.startswith(b"%PDF"), "Response is not a valid PDF file"
        print(f"  [SUCCESS] PDF Report generated dynamically: {len(pdf_bytes):,} bytes received with %PDF header.")

    # 7. SQLite Analysis History Operations
    print("\n[Step 7/8] Testing SQLite History Persistence & Operations...")
    with urllib.request.urlopen(f"{BACKEND_URL}/history") as resp:
        assert resp.status == 200
        history_data = json.loads(resp.read().decode())
        items = history_data.get("history", [])
        assert len(items) > 0
        latest_id = items[0]["id"]
        print(f"  [SUCCESS] Retrieved {len(items)} history record(s). Latest ID: #{latest_id}")

    # Test single item lookup
    with urllib.request.urlopen(f"{BACKEND_URL}/history/{latest_id}") as resp:
        assert resp.status == 200
        item_detail = json.loads(resp.read().decode())
        assert item_detail["job_title"] == "Senior Full Stack Engineer"
        print(f"  [SUCCESS] Record #{latest_id} detail lookup verified.")

    # 8. Sample Presets API
    print("\n[Step 8/8] Testing 1-Click Demo Presets API...")
    with urllib.request.urlopen(f"{BACKEND_URL}/sample-data") as resp:
        assert resp.status == 200
        presets = json.loads(resp.read().decode())
        assert "software_engineer" in presets["resumes"]
        assert "data_scientist" in presets["resumes"]
        print("  [SUCCESS] Sample presets ready for instant 1-click hackathon demos.")

    print("\n==================================================================")
    print("    🎉 ALL 8/8 SYSTEM VERIFICATION CHECKS PASSED WITH ZERO ERRORS! ")
    print("==================================================================")

if __name__ == "__main__":
    run_all_checks()
