"""
Live integration test against running Flask server at http://127.0.0.1:5000
"""
import sys
import urllib.request
import urllib.parse
import json
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000/api"

def test_live_health():
    print("[1/5] Testing /api/health...")
    with urllib.request.urlopen(f"{BASE_URL}/health") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        print("  [PASS] Health Response:", data["status"], "| Model:", data["ai_model"])

def test_live_sample_data():
    print("[2/5] Testing /api/sample-data...")
    with urllib.request.urlopen(f"{BASE_URL}/sample-data") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert "resumes" in data
        assert "job_descriptions" in data
        print("  [PASS] Loaded sample presets successfully.")
        return data

def test_live_analysis(sample_data):
    print("[3/5] Testing /api/analyze...")
    resume = sample_data["resumes"]["software_engineer"]["text"]
    job = sample_data["job_descriptions"]["software_engineer"]["text"]
    
    payload = json.dumps({
        "resume_text": resume,
        "job_description": job,
        "job_title": "Lead Software Engineer",
        "force_demo": True
    }).encode("utf-8")
    
    req = urllib.request.Request(
        f"{BASE_URL}/analyze",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        result = json.loads(resp.read().decode())
        print(f"  [PASS] Overall Score: {result['scores']['overall']}/100")
        print(f"  [PASS] Matched Skills: {len(result['skills_matched'])} -> {result['skills_matched'][:4]}")
        print(f"  [PASS] Missing Skills: {len(result['skills_missing'])} -> {result['skills_missing'][:4]}")
        print(f"  [PASS] Analysis ID: {result.get('analysis_id')}")
        return result

def test_live_pdf_generation(analysis_result):
    print("[4/5] Testing /api/generate-pdf...")
    payload = json.dumps({"analysis_data": analysis_result}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/generate-pdf",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        pdf_bytes = resp.read()
        assert pdf_bytes.startswith(b"%PDF")
        print(f"  [PASS] Generated PDF Report of length: {len(pdf_bytes)} bytes.")

def test_live_history(analysis_id):
    print("[5/5] Testing /api/history...")
    with urllib.request.urlopen(f"{BASE_URL}/history") as resp:
        assert resp.status == 200
        history_data = json.loads(resp.read().decode())
        items = history_data.get("history", [])
        print(f"  [PASS] History contains {len(items)} record(s).")
        assert any(item["id"] == analysis_id for item in items)

if __name__ == "__main__":
    print("=== RUNNING LIVE E2E INTEGRATION VERIFICATION ===")
    test_live_health()
    sample = test_live_sample_data()
    result = test_live_analysis(sample)
    test_live_pdf_generation(result)
    test_live_history(result["analysis_id"])
    print("=== ALL 5 LIVE INTEGRATION CHECKS PASSED PERFECTLY! ===")
