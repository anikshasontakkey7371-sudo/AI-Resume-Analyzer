"""
Resume Analyzer Service.
Provides multi-criteria ATS matching and feedback via:
1. Live AI Integration (Google Gemini LLM via GEMINI_API_KEY)
2. Transparent Rule-Based Engine (Demo Mode with deterministic keyword matching)
"""
import os
import sys
import re
import json
import logging
from typing import Optional, Dict, Any, Set, List

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

try:
    from config import Config
except ImportError:
    from backend.config import Config

logger = logging.getLogger(__name__)

# Comprehensive Skill & Keyword Taxonomy
SKILL_TAXONOMY = {
    "languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css", "bash", "shell"
    ],
    "frameworks_and_libraries": [
        "react", "react.js", "next.js", "vue", "vue.js", "angular", "node.js", "express", "express.js",
        "django", "flask", "fastapi", "spring", "spring boot", "asp.net", "laravel",
        "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "opencv",
        "tailwind", "tailwindcss", "bootstrap", "sass", "redux", "graphql", "rest api", "restful api"
    ],
    "databases_and_storage": [
        "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis", "elasticsearch",
        "dynamodb", "cassandra", "firebase", "supabase", "mariadb", "oracle"
    ],
    "cloud_and_devops": [
        "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ci/cd", "github actions", "gitlab ci", "jenkins", "ansible", "nginx", "linux"
    ],
    "tools_and_practices": [
        "git", "github", "gitlab", "jira", "agile", "scrum", "microservices", "unit testing",
        "pytest", "jest", "cypress", "system design", "oop", "object oriented programming",
        "data structures", "algorithms", "tdd", "api design"
    ],
    "soft_skills": [
        "leadership", "teamwork", "communication", "problem solving", "critical thinking",
        "collaboration", "adaptability", "project management", "time management", "mentorship",
        "cross-functional collaboration", "analytical skills"
    ]
}

# Strong action verbs for active voice and leadership evaluation
STRONG_ACTION_VERBS = [
    "spearheaded", "engineered", "architected", "developed", "designed", "implemented",
    "optimized", "accelerated", "scaled", "automated", "streamlined", "orchestrated",
    "reduced", "increased", "boosted", "maximized", "championed", "delivered",
    "collaborated", "mentored", "revamped", "transformed", "solved"
]

COMMON_RESUME_SECTIONS = [
    "education", "experience", "work experience", "projects", "skills",
    "technical skills", "certifications", "contact", "summary", "objective"
]

class ResumeAnalyzer:
    """Service to evaluate resumes against job requisitions."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize text for analysis."""
        text = text.lower()
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'[^\w\s\+\#\.\-]', ' ', text)
        return ' '.join(text.split())

    @classmethod
    def extract_skills(cls, text: str) -> Set[str]:
        """Extract taxonomy skills from raw text."""
        cleaned = cls.clean_text(text)
        found_skills = set()
        
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                escaped = re.escape(skill)
                if skill in ["c++", "c#", ".net"]:
                    pattern = rf'(?:^|\s){escaped}(?:$|\s)'
                else:
                    pattern = rf'\b{escaped}\b'
                    
                if re.search(pattern, cleaned):
                    found_skills.add(skill)
                    
        return found_skills

    @classmethod
    def extract_bullets(cls, text: str) -> List[str]:
        """Extract candidate bullet points from resume text."""
        lines = text.split('\n')
        bullets = []
        for line in lines:
            stripped = line.strip()
            if re.match(r'^[\u2022\u2023\u25E6\u2043\u2219\*\-\–\—\d+\.]\s*', stripped):
                cleaned_bullet = re.sub(r'^[\u2022\u2023\u25E6\u2043\u2219\*\-\–\—\d+\.]\s*', '', stripped)
                if len(cleaned_bullet.split()) >= 4:
                    bullets.append(cleaned_bullet)
            elif len(stripped.split()) >= 6 and any(stripped.lower().startswith(v) for v in STRONG_ACTION_VERBS):
                bullets.append(stripped)
        return bullets

    @classmethod
    def analyze_rule_based(cls, resume_text: str, job_description: str, job_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Deterministic, explainable rule-based matching engine (Demo Mode).
        Computes genuine mathematical scores based on skills, keyword density,
        experience metrics, and resume structure.
        """
        resume_skills = cls.extract_skills(resume_text)
        jd_skills = cls.extract_skills(job_description)
        
        if not jd_skills:
            jd_words = [w for w in cls.clean_text(job_description).split() if len(w) > 4]
            jd_skills = set(jd_words[:12])
            
        matched_skills = sorted(list(resume_skills.intersection(jd_skills)))
        missing_skills = sorted(list(jd_skills - resume_skills))
        extra_resume_skills = sorted(list(resume_skills - jd_skills))
        
        # 1. Skills Match Score (Weight: 40%)
        if jd_skills:
            skills_ratio = len(matched_skills) / len(jd_skills)
            bonus = min(0.15, len(extra_resume_skills) * 0.02)
            raw_skills_score = min(1.0, skills_ratio + bonus) * 100
        else:
            raw_skills_score = 75.0
        skills_score = round(raw_skills_score, 1)

        # 2. ATS Keyword Coverage Score (Weight: 20%)
        jd_clean = cls.clean_text(job_description)
        resume_clean = cls.clean_text(resume_text)
        
        stop_words = {
            "about", "above", "after", "again", "against", "all", "and", "any", "are", "because",
            "been", "before", "being", "below", "between", "both", "but", "by", "can", "cannot",
            "could", "did", "does", "doing", "down", "during", "each", "few", "for", "from",
            "further", "had", "has", "have", "having", "her", "here", "hers", "herself", "him",
            "himself", "his", "how", "into", "its", "itself", "more", "most", "must", "myself",
            "nor", "not", "off", "once", "only", "other", "ought", "our", "ours", "ourselves",
            "out", "over", "own", "same", "she", "should", "some", "such", "than", "that", "the",
            "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this",
            "those", "through", "too", "under", "until", "very", "was", "were", "what", "when",
            "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your",
            "role", "work", "team", "years", "candidate", "experience", "preferred", "qualifications"
        }
        
        jd_tokens = [w for w in re.findall(r'\b[a-z]{3,}\b', jd_clean) if w not in stop_words]
        token_freq = {}
        for t in jd_tokens:
            token_freq[t] = token_freq.get(t, 0) + 1
            
        top_jd_keywords = sorted(token_freq.items(), key=lambda x: x[1], reverse=True)[:25]
        matched_keywords = []
        missing_keywords = []
        
        for kw, freq in top_jd_keywords:
            if kw in resume_clean:
                matched_keywords.append({"keyword": kw, "importance": "High" if freq > 2 else "Medium"})
            else:
                missing_keywords.append({"keyword": kw, "importance": "High" if freq > 2 else "Medium"})
                
        if top_jd_keywords:
            keyword_score = round((len(matched_keywords) / len(top_jd_keywords)) * 100, 1)
        else:
            keyword_score = 70.0

        # 3. Experience Relevance & Impact Score (Weight: 25%)
        metric_matches = re.findall(r'\b\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?|\b\d{2,}\b', resume_text)
        metric_count = len(metric_matches)
        action_verb_count = sum(1 for verb in STRONG_ACTION_VERBS if re.search(rf'\b{verb}\b', resume_clean))
        
        experience_points = 50
        if metric_count >= 5:
            experience_points += 25
        elif metric_count >= 2:
            experience_points += 15
        else:
            experience_points += 5
            
        if action_verb_count >= 6:
            experience_points += 25
        elif action_verb_count >= 3:
            experience_points += 15
        else:
            experience_points += 5
            
        experience_score = min(100.0, float(experience_points))

        # 4. Formatting and Readability Score (Weight: 15%)
        word_count = len(resume_text.split())
        sections_found = [s for s in COMMON_RESUME_SECTIONS if s in resume_clean]
        
        format_points = 50
        if 300 <= word_count <= 950:
            format_points += 25
        elif 150 <= word_count < 300 or 950 < word_count <= 1400:
            format_points += 15
        else:
            format_points += 5
            
        if len(sections_found) >= 4:
            format_points += 25
        elif len(sections_found) >= 2:
            format_points += 15
        else:
            format_points += 5
            
        formatting_score = min(100.0, float(format_points))

        # Calculate Overall Weighted Score
        overall_score = round(
            (skills_score * Config.WEIGHT_SKILLS) +
            (experience_score * Config.WEIGHT_EXPERIENCE) +
            (keyword_score * Config.WEIGHT_KEYWORDS) +
            (formatting_score * Config.WEIGHT_FORMATTING)
        )
        overall_score = max(10, min(99, overall_score))

        # Strengths Analysis
        strengths = []
        if len(matched_skills) >= 4:
            strengths.append(f"Demonstrates strong coverage in key requested technical skills: {', '.join(matched_skills[:4])}.")
        if metric_count >= 3:
            strengths.append("Effective use of quantifiable metrics and measurable outcomes to prove past accomplishments.")
        if action_verb_count >= 4:
            strengths.append("Active voice utilized with decisive action verbs emphasizing leadership and technical execution.")
        if len(sections_found) >= 3:
            strengths.append(f"Clear structural organization including expected sections ({', '.join(sections_found[:3])}).")
        if not strengths:
            strengths.append("Foundational background relevant to the target domain is present in the resume text.")

        # Areas that need improvement
        improvements = []
        if missing_skills:
            improvements.append(f"Incorporate missing core competencies prominently: {', '.join(missing_skills[:5])}.")
        if metric_count < 3:
            improvements.append("Increase numerical evidence (percentages, user counts, performance gains) in project bullet points.")
        if action_verb_count < 4:
            improvements.append("Replace passive descriptions (e.g. 'Responsible for', 'Assisted with') with high-impact action verbs.")
        if word_count < 250:
            improvements.append("Resume content is sparse. Expand on key responsibilities, technical stacks used, and outcomes.")
        elif word_count > 1000:
            improvements.append("Resume is lengthy. Condense descriptions into tight, scannable bullet points suitable for a 1-page format.")
        if not improvements:
            improvements.append("Fine-tune terminology to match the exact phrasing used in the target job description.")

        # Bullet point rewrites (STAR method suggestions)
        raw_bullets = cls.extract_bullets(resume_text)
        bullet_suggestions = []
        
        if raw_bullets:
            for b in raw_bullets[:3]:
                bullet_suggestions.append({
                    "original": b,
                    "improved": f"Engineered and deployed a scalable solution using {matched_skills[0] if matched_skills else 'modern architecture'}, improving efficiency by 25% and reducing processing latency.",
                    "reason": "Replaced passive phrasing with an action verb, named specific technologies, and injected a measurable result."
                })
        else:
            bullet_suggestions = [
                {
                    "original": "Worked on backend features and fixed bugs for the application.",
                    "improved": "Engineered robust RESTful backend APIs with automated error-handling, reducing production bug reports by 30% across 5,000+ active users.",
                    "reason": "Quantifies scale and demonstrates direct business and architectural impact."
                },
                {
                    "original": "Helped team build database schemas and queries.",
                    "improved": "Optimized complex PostgreSQL database queries and indexing strategies, achieving a 40% reduction in query execution times.",
                    "reason": "Showcases specific database technology and tangible speed optimization."
                }
            ]

        # Recommended skills roadmap
        recommended_skills = []
        for skill in missing_skills[:6]:
            recommended_skills.append({
                "skill": skill.capitalize(),
                "priority": "High" if skill in [m["keyword"] for m in missing_keywords[:3]] else "Medium",
                "suggestion": f"Build a focused mini-project showcasing {skill.capitalize()} integration with your existing stack ({matched_skills[0].capitalize() if matched_skills else 'Python'})."
            })
            
        if not recommended_skills:
            recommended_skills = [
                {"skill": "System Design & Architecture", "priority": "Medium", "suggestion": "Study distributed systems patterns, caching strategies, and microservice decoupling."},
                {"skill": "CI/CD & Cloud Deployment", "priority": "Medium", "suggestion": "Set up GitHub Actions automated testing and deployment to AWS or GCP."}
            ]

        role_title = job_title or "Target Role"
        summary_text = (
            f"Your resume achieves a {overall_score}/100 alignment with the {role_title} role. "
            f"You successfully match {len(matched_skills)} core skills ({', '.join(matched_skills[:3]) if matched_skills else 'fundamental areas'}), "
            f"with {len(missing_skills)} key technical competencies recommended for inclusion to maximize interview callbacks."
        )

        return {
            "analysis_mode": "Transparent Rule Engine (Demo)",
            "is_ai_powered": False,
            "target_role": role_title,
            "summary": summary_text,
            "scores": {
                "overall": overall_score,
                "skills_match": skills_score,
                "experience_relevance": experience_score,
                "keyword_coverage": keyword_score,
                "formatting_readability": formatting_score
            },
            "transparent_criteria": {
                "skills_weight": f"{int(Config.WEIGHT_SKILLS * 100)}%",
                "experience_weight": f"{int(Config.WEIGHT_EXPERIENCE * 100)}%",
                "keyword_weight": f"{int(Config.WEIGHT_KEYWORDS * 100)}%",
                "formatting_weight": f"{int(Config.WEIGHT_FORMATTING * 100)}%",
                "explanation": "Calculated deterministically using token overlap, skill taxonomy indexing, quantifiable metric frequency, action verb density, and ATS formatting standards.",
                "disclaimer": "This score is an algorithmic estimate based on provided criteria and does not guarantee ATS passage or hiring selection."
            },
            "skills_matched": matched_skills,
            "skills_missing": missing_skills,
            "skills_additional": extra_resume_skills[:8],
            "strengths": strengths,
            "improvements": improvements,
            "bullet_point_suggestions": bullet_suggestions,
            "ats_keywords": {
                "matched": [m["keyword"] for m in matched_keywords[:8]],
                "missing": [m["keyword"] for m in missing_keywords[:8]],
                "recommendation": "Integrate missing keywords naturally into your Work Experience bullet points and Skills section."
            },
            "formatting_feedback": {
                "word_count": word_count,
                "word_count_status": "Ideal (300-900 words)" if 300 <= word_count <= 950 else "Check Length",
                "sections_detected": sections_found,
                "action_verb_count": action_verb_count,
                "metrics_detected": metric_count,
                "notes": "Good section structure detected. Ensure consistent date formatting (e.g. Month Year - Month Year) and clean bullet formatting."
            },
            "recommended_skills_to_learn": recommended_skills
        }

    @classmethod
    def analyze_with_gemini(cls, resume_text: str, job_description: str, job_title: Optional[str] = None) -> Dict[str, Any]:
        """Call Google Gemini API using google-genai SDK."""
        from google import genai
        from google.genai import types

        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not configured.")

        client = genai.Client(api_key=api_key)
        role_context = f"for the role of '{job_title}'" if job_title else "for the provided job description"

        prompt = f"""
You are an expert ATS (Applicant Tracking System) engineer, hiring director, and professional career coach.
Analyze the following resume against the target job description {role_context}.

Resume Text:
\"\"\"
{resume_text[:4000]}
\"\"\"

Job Description:
\"\"\"
{job_description[:3000]}
\"\"\"

Provide your analysis strictly in the following JSON format without any markdown backticks or commentary outside the JSON:
{{
  "analysis_mode": "AI-Powered Analysis (Gemini)",
  "is_ai_powered": true,
  "target_role": "{job_title or 'Target Role'}",
  "summary": "2-3 sentence executive summary of candidate suitability and key gap",
  "scores": {{
    "overall": 78,
    "skills_match": 80,
    "experience_relevance": 75,
    "keyword_coverage": 70,
    "formatting_readability": 85
  }},
  "transparent_criteria": {{
    "skills_weight": "40%",
    "experience_weight": "25%",
    "keyword_weight": "20%",
    "formatting_weight": "15%",
    "explanation": "Weighted synthesis based on hard/soft skill parity, depth of demonstrated experience, keyword coverage, and ATS structural compliance.",
    "disclaimer": "This score is an objective AI estimate and does not guarantee ATS selection or interview invitations."
  }},
  "skills_matched": ["skill1", "skill2"],
  "skills_missing": ["missing1", "missing2"],
  "skills_additional": ["extra1", "extra2"],
  "strengths": [
    "Specific strength with clear reason",
    "Another specific strength"
  ],
  "improvements": [
    "Actionable area for improvement",
    "Another actionable area"
  ],
  "bullet_point_suggestions": [
    {{
      "original": "Weak bullet point from candidate resume or representative weakness",
      "improved": "Rewritten bullet point using Action Verb + Context + Quantifiable Metric (STAR method)",
      "reason": "Explanation of why this rewrite works better for recruiters and ATS"
    }}
  ],
  "ats_keywords": {{
    "matched": ["keyword1", "keyword2"],
    "missing": ["keyword3", "keyword4"],
    "recommendation": "Advice on where and how to incorporate missing keywords naturally"
  }},
  "formatting_feedback": {{
    "word_count_status": "Appropriate / Too Short / Too Long",
    "sections_detected": ["Education", "Experience", "Skills"],
    "action_verb_count": 8,
    "metrics_detected": 4,
    "notes": "Actionable feedback on layout, bullet structure, and readability"
  }},
  "recommended_skills_to_learn": [
    {{
      "skill": "Skill Name",
      "priority": "High/Medium",
      "suggestion": "Recommended practical learning roadmap or project"
    }}
  ]
}}
"""

        response = client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )

        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        data = json.loads(result_text)
        data["analysis_mode"] = "AI-Powered Analysis (Gemini)"
        data["is_ai_powered"] = True
        return data

    @classmethod
    def analyze(cls, resume_text: str, job_description: str, job_title: Optional[str] = None, force_demo: bool = False) -> Dict[str, Any]:
        """
        Unified analysis entrypoint.
        Routes to Gemini if key is present and not forced to demo;
        otherwise runs transparent rule-based engine.
        """
        if not force_demo and Config.is_ai_configured():
            try:
                logger.info("Executing Gemini AI analysis...")
                return cls.analyze_with_gemini(resume_text, job_description, job_title)
            except Exception as e:
                logger.warning(f"AI service call failed ({str(e)}). Falling back to transparent rule engine.")
                fallback = cls.analyze_rule_based(resume_text, job_description, job_title)
                fallback["warning"] = f"AI service unavailable ({str(e)}). Result computed using Transparent Rule Engine."
                return fallback
        else:
            logger.info("Executing transparent rule-based analysis (Demo Mode)...")
            return cls.analyze_rule_based(resume_text, job_description, job_title)
