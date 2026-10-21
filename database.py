"""
SQLite database management for AI Resume Analyzer history.
Only stores analysis metrics and structured feedback.
Does NOT store raw uploaded resume files.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "resume_history.db")

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            job_title TEXT NOT NULL,
            overall_score INTEGER NOT NULL,
            skills_score INTEGER NOT NULL,
            experience_score INTEGER NOT NULL,
            keyword_score INTEGER NOT NULL,
            formatting_score INTEGER NOT NULL,
            matched_count INTEGER NOT NULL,
            missing_count INTEGER NOT NULL,
            analysis_mode TEXT NOT NULL,
            summary TEXT,
            result_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(job_title: str, result: Dict[str, Any], mode: str = "Rule Engine") -> int:
    """Save analysis record and return inserted ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = job_title or result.get("target_role") or "General Position"
    
    scores = result.get("scores", {})
    overall_score = int(scores.get("overall", 0))
    skills_score = int(scores.get("skills_match", 0))
    experience_score = int(scores.get("experience_relevance", 0))
    keyword_score = int(scores.get("keyword_coverage", 0))
    formatting_score = int(scores.get("formatting_readability", 0))
    
    matched_skills = result.get("skills_matched", [])
    missing_skills = result.get("skills_missing", [])
    
    summary = result.get("summary", "")
    result_json_str = json.dumps(result)
    
    cursor.execute("""
        INSERT INTO analyses (
            created_at, job_title, overall_score, skills_score,
            experience_score, keyword_score, formatting_score,
            matched_count, missing_count, analysis_mode,
            summary, result_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        created_at, title, overall_score, skills_score,
        experience_score, keyword_score, formatting_score,
        len(matched_skills), len(missing_skills), mode,
        summary, result_json_str
    ))
    
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_history(limit: int = 30) -> List[Dict[str, Any]]:
    """Retrieve recent analysis history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, job_title, overall_score, skills_score,
               experience_score, keyword_score, formatting_score,
               matched_count, missing_count, analysis_mode, summary
        FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single complete analysis by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    data = dict(row)
    try:
        data["result"] = json.loads(data["result_json"])
    except Exception:
        data["result"] = {}
    return data

def delete_analysis(analysis_id: int) -> bool:
    """Delete a single analysis record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def clear_history() -> int:
    """Delete all analysis records from history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count
