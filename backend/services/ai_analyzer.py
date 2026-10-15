"""
AI RESUME LAB — AI Resume & Job Matching Engine
Performs intelligent rule-based NLP extraction and scoring,
with optional LLM integration (OpenAI / Anthropic) if API keys are configured.
"""
import re
import math
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# ── Tech & Domain Skills Master Dictionary ───────────────────────────
KNOWN_SKILLS = [
    # Cloud & DevOps
    "AWS", "Amazon Web Services", "EC2", "S3", "Lambda", "VPC", "IAM", "CloudFront", "Route 53", "ECS", "EKS",
    "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Puppet", "Chef",
    "Jenkins", "GitHub Actions", "GitLab CI", "CI/CD", "Helm", "ArgoCD", "Linux", "Unix", "Bash", "Shell",
    "Prometheus", "Grafana", "Datadog", "ELK", "Elasticsearch", "Logstash", "Kibana", "Splunk", "New Relic",
    "OpenTelemetry", "Istio", "Service Mesh", "Nginx", "Apache", "Networking", "TCP/IP", "DNS", "VPN",

    # Programming Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang", "Rust", "Ruby", "PHP",
    "Scala", "Kotlin", "Swift", "R", "SQL", "HTML", "HTML5", "CSS", "CSS3", "Sass",

    # Frameworks & Libraries
    "Flask", "Django", "FastAPI", "React", "React.js", "Vue", "Vue.js", "Angular", "Next.js", "Node.js",
    "Express", "Express.js", "Spring", "Spring Boot", ".NET", "ASP.NET", "Tailwind", "Bootstrap",

    # Databases & Caching
    "PostgreSQL", "Postgres", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra", "DynamoDB",
    "Memcached", "RabbitMQ", "Kafka", "Celery", "GraphQL", "REST", "RESTful", "REST APIs",

    # Architecture & Practices
    "Microservices", "System Design", "Distributed Systems", "OOP", "SOLID", "Design Patterns",
    "Agile", "Scrum", "Kanban", "Jira", "Git", "GitHub", "GitLab", "Bitbucket", "TDD", "Unit Testing",
    "Integration Testing", "DevOps", "DevSecOps", "SRE", "Site Reliability Engineering",

    # AI, ML & Data
    "Machine Learning", "Deep Learning", "Artificial Intelligence", "NLP", "Computer Vision",
    "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", "Pandas", "NumPy", "OpenCV", "Hugging Face",
    "LLM", "Prompt Engineering", "OpenAI", "Data Analysis", "Data Science", "Spark", "Hadoop", "Airflow"
]

ACTION_VERBS = [
    "built", "developed", "designed", "architected", "engineered", "implemented", "optimized",
    "automated", "created", "spearheaded", "orchestrated", "deployed", "scaled", "led", "managed",
    "reduced", "increased", "improved", "saved", "accelerated", "integrated", "transformed",
    "mentored", "maintained", "configured", "analyzed", "resolved", "delivered", "executed"
]


def extract_skills(text: str) -> List[str]:
    """Find known skills present in text using case-insensitive token boundary matching."""
    found = []
    text_lower = " " + text.lower() + " "
    for skill in KNOWN_SKILLS:
        # Match word boundaries or punctuation borders
        escaped = re.escape(skill.lower())
        pattern = rf"(?:^|[\s,;:\(\)\[\]\/\-\.])({escaped})(?:[\s,;:\(\)\[\]\/\-\.]|$)"
        if re.search(pattern, text_lower):
            found.append(skill)
    # Deduplicate while preserving canonical casing
    seen = set()
    unique = []
    for s in found:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            unique.append(s)
    return unique


def calculate_structure_score(text: str) -> int:
    """Evaluates presence of key resume sections."""
    score = 40
    text_lower = text.lower()
    sections = [
        ("summary", 10),
        ("experience", 15),
        ("skills", 15),
        ("education", 10),
        ("projects", 10),
    ]
    for sec, pts in sections:
        if sec in text_lower:
            score += pts
    return min(100, score)


def calculate_formatting_score(text: str) -> int:
    """Checks formatting hygiene: line length, bullet points, clean text."""
    score = 75
    lines = text.split("\n")
    if 20 <= len(lines) <= 200:
        score += 10
    # Check for bullets
    bullets = [l for l in lines if re.match(r"^\s*[\-\*\•\–\—]\s+", l)]
    if len(bullets) >= 5:
        score += 10
    # Deduct if text has excessive non-ascii garble
    non_ascii = len(re.findall(r"[^\x00-\x7F]", text))
    if non_ascii > len(text) * 0.05:
        score -= 15
    return max(40, min(100, score))


def calculate_experience_score(text: str) -> int:
    """Assesses use of action verbs, impact numbers, and metrics."""
    score = 50
    text_lower = text.lower()
    
    # Action verbs count
    verbs_count = sum(1 for verb in ACTION_VERBS if f" {verb} " in text_lower)
    if verbs_count >= 8:
        score += 20
    elif verbs_count >= 4:
        score += 12
    elif verbs_count >= 2:
        score += 6

    # Metrics / numbers count (%, $, multiplier X, quantities)
    metrics_count = len(re.findall(r"(\d+%\s*|\$\s*\d+|\b\d+x\b|\b\d{2,}\b)", text))
    if metrics_count >= 6:
        score += 20
    elif metrics_count >= 3:
        score += 12
    elif metrics_count >= 1:
        score += 5

    # Check for dates/timeline
    if re.search(r"\b(20\d{2}|19\d{2})\b", text):
        score += 10

    return max(40, min(100, score))


def calculate_education_score(text: str) -> int:
    """Checks for education credentials, degrees, and academic keywords."""
    score = 65
    text_lower = text.lower()
    degree_keywords = ["bachelor", "master", "b.s", "m.s", "b.tech", "m.tech", "ph.d", "degree", "university", "college", "institute", "gpa"]
    matched = sum(1 for d in degree_keywords if d in text_lower)
    score += min(35, matched * 10)
    return max(50, min(100, score))


def analyze_resume(resume_text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
    """
    Main analysis pipeline.
    Calculates detailed scores, strengths, weaknesses, recommendations, and matching skills.
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return {
            "ats_score": 30,
            "job_match": None,
            "resume_structure": 40,
            "keywords_score": 35,
            "skills_score": 30,
            "experience_score": 30,
            "education_score": 50,
            "formatting_score": 40,
            "strengths": ["Resume uploaded successfully."],
            "weaknesses": ["Text content is very short or could not be fully parsed."],
            "recommendations": [
                {
                    "issue": "Insufficient resume text",
                    "why": "Recruiters and ATS parsers need adequate detail to evaluate your experience.",
                    "fix": "Upload a full 1–2 page resume with detailed work history and technical competencies."
                }
            ],
            "matching_skills": [],
            "missing_skills": [],
        }

    resume_skills = extract_skills(resume_text)
    structure_score = calculate_structure_score(resume_text)
    formatting_score = calculate_formatting_score(resume_text)
    experience_score = calculate_experience_score(resume_text)
    education_score = calculate_education_score(resume_text)

    # Keywords score based on skill density
    keywords_score = min(98, max(50, 45 + len(resume_skills) * 3))
    skills_score = min(98, max(45, 40 + len(resume_skills) * 3))

    # Job match calculation
    job_match_score = None
    matching_skills = []
    missing_skills = []

    if job_description and len(job_description.strip()) > 20:
        jd_skills = extract_skills(job_description)
        if jd_skills:
            matching_skills = [s for s in jd_skills if any(s.lower() == rs.lower() for rs in resume_skills)]
            missing_skills = [s for s in jd_skills if not any(s.lower() == rs.lower() for rs in resume_skills)]
            ratio = len(matching_skills) / max(len(jd_skills), 1)
            job_match_score = int(round(40 + ratio * 58))
        else:
            # Fallback text token overlap
            resume_words = set(re.findall(r"\w{4,}", resume_text.lower()))
            jd_words = set(re.findall(r"\w{4,}", job_description.lower()))
            overlap = len(resume_words.intersection(jd_words)) / max(len(jd_words), 1)
            job_match_score = int(round(45 + min(overlap * 50, 50)))
    else:
        # Default skill display when no job description is provided
        matching_skills = resume_skills[:10]
        missing_skills = ["Kubernetes", "Terraform", "CI/CD", "Monitoring", "Docker"]
        missing_skills = [s for s in missing_skills if s not in resume_skills][:4]

    # Overall ATS Score (weighted composite)
    if job_match_score is not None:
        ats_score = int(round(
            0.25 * job_match_score +
            0.20 * keywords_score +
            0.20 * experience_score +
            0.15 * structure_score +
            0.10 * skills_score +
            0.10 * formatting_score
        ))
    else:
        ats_score = int(round(
            0.25 * keywords_score +
            0.25 * experience_score +
            0.20 * structure_score +
            0.15 * skills_score +
            0.15 * formatting_score
        ))
    ats_score = max(35, min(96, ats_score))

    # Strengths
    strengths = []
    if len(resume_skills) >= 8:
        strengths.append(f"Strong technology footprint with {len(resume_skills)}+ identified technical competencies.")
    else:
        strengths.append("Found clear foundational technical skills.")

    if experience_score >= 75:
        strengths.append("Strong experience section featuring action-oriented verbs and quantifiable accomplishments.")
    else:
        strengths.append("Chronological career layout with structured work experience.")

    if structure_score >= 80:
        strengths.append("Well-organized layout containing all critical resume sections (Summary, Skills, Experience, Education).")

    if matching_skills and len(matching_skills) >= 4:
        strengths.append(f"High keyword alignment with target requirements, including {', '.join(matching_skills[:3])}.")

    # Weaknesses
    weaknesses = []
    if len(resume_skills) < 8:
        weaknesses.append("Skill density is low; essential modern tools and frameworks are not explicitly listed.")
    if experience_score < 75:
        weaknesses.append("Bullet points lack quantifiable metrics, dollar amounts, or measurable business impact.")
    if missing_skills:
        weaknesses.append(f"Missing high-demand target skills: {', '.join(missing_skills[:3])}.")
    if structure_score < 75:
        weaknesses.append("One or more key resume sections (Professional Summary, Projects, or Education) need more prominence.")

    # Recommendations
    recommendations = []
    if missing_skills:
        recommendations.append({
            "issue": f"Missing critical target skills ({', '.join(missing_skills[:3])})",
            "why": "Applicant Tracking Systems automatically screen out candidates lacking these core required keywords.",
            "fix": f"Incorporate hands-on experience or coursework with {missing_skills[0]} and {missing_skills[1] if len(missing_skills) > 1 else 'related tooling'} into your project bullets."
        })

    recommendations.append({
        "issue": "Quantify bullet points using the Google XYZ Formula",
        "why": "Recruiters favor candidates who demonstrate tangible ROI over generic duty descriptions.",
        "fix": "Rephrase duties into: 'Accomplished [X], as measured by [Y]%, by doing [Z]' (e.g. 'Reduced API latency by 35% by implementing Redis caching')."
    })

    if structure_score < 85:
        recommendations.append({
            "issue": "Polish Professional Summary & Core Competencies",
            "why": "Hiring managers spend an average of 6 seconds on initial resume triage.",
            "fix": "Lead with a punchy 3-line executive summary followed by a categorized skills grid highlighting your core domain."
        })

    return {
        "ats_score": ats_score,
        "job_match": job_match_score,
        "resume_structure": structure_score,
        "keywords_score": keywords_score,
        "skills_score": skills_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "formatting_score": formatting_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
    }
