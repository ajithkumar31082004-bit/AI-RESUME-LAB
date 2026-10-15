"""
AI RESUME LAB — AI Resume Content & Bullet Optimizer
Rewrites summaries, optimizes bullet points using Google's XYZ formula,
generates headlines, and extracts high-impact keywords.
"""
from flask import Blueprint, request, jsonify
import re
import random

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/improve-summary", methods=["POST"])
def improve_summary():
    """
    Transforms a generic resume summary into an executive, high-converting elevator pitch.
    Input: { summary: str, job_title: str }
    """
    data = request.get_json() or {}
    summary = (data.get("summary") or "").strip()
    job_title = (data.get("job_title") or "Software / Cloud Engineer").strip()

    if not summary:
        return jsonify({"message": "summary is required"}), 400

    # Extract years of experience if mentioned
    years_match = re.search(r"(\d+)\+?\s*years?", summary, re.IGNORECASE)
    years = years_match.group(0) if years_match else "3+ years"

    improved = (
        f"Results-driven {job_title} with {years} of proven experience architecting, automating, "
        f"and scaling resilient distributed systems and cloud infrastructure. Demonstrated expertise in driving "
        f"99.99% system availability, streamlining CI/CD deployment pipelines, and reducing infrastructure operational overhead. "
        f"Adept at cross-functional collaboration and translating complex technical requirements into high-impact business solutions."
    )

    return jsonify({
        "original_summary": summary,
        "improved_summary": improved,
        "key_enhancements": [
            "Introduced active executive voice and quantifiable credibility",
            "Front-loaded target role keywords for rapid ATS discovery",
            "Emphasized measurable business outcomes and operational reliability"
        ],
        "keywords_added": ["High Availability (99.99%)", "CI/CD Automation", "Infrastructure Optimization", "Distributed Systems"]
    }), 200


@ai_bp.route("/rewrite-experience", methods=["POST"])
def rewrite_experience():
    """
    Rewrites plain job experience bullets into high-impact Google XYZ statements:
    Accomplished [X], as measured by [Y], by doing [Z].
    Input: { experience: str }
    """
    data = request.get_json() or {}
    experience = (data.get("experience") or "").strip()

    if not experience:
        return jsonify({"message": "experience text is required"}), 400

    raw_bullets = [b.strip().lstrip("-*• ") for b in experience.split("\n") if b.strip()]
    if not raw_bullets:
        raw_bullets = [experience]

    rewritten = []
    templates = [
        "Architected and deployed {topic}, reducing latency by 38% and boosting throughput across 50,000+ daily active users.",
        "Automated deployment workflows for {topic}, slashing release cycle duration from 2 hours to 12 minutes with zero downtime.",
        "Engineered resilient data pipelines around {topic}, eliminating 95% of manual operational tasks and improving data accuracy.",
        "Optimized resource provisioning for {topic}, decreasing monthly cloud infrastructure expenditures by 28% without sacrificing SLA.",
        "Spearheaded end-to-end integration of {topic}, accelerating customer onboarding time by 45% across distributed engineering teams."
    ]

    for i, b in enumerate(raw_bullets):
        topic = b.rstrip(".")
        template = templates[i % len(templates)]
        formatted = template.format(topic=topic)
        rewritten.append({
            "original": b,
            "optimized": formatted,
            "metric_type": "Efficiency & Cost Reduction" if i % 2 == 0 else "Speed & Reliability"
        })

    return jsonify({
        "formula": "Google XYZ Formula (Accomplished [X] measured by [Y] by doing [Z])",
        "bullets": rewritten
    }), 200


@ai_bp.route("/generate-headline", methods=["POST"])
def generate_headline():
    """
    Generates compelling LinkedIn & Resume headlines tailored to candidate skills.
    Input: { name: str, skills: list[str] or str, experience: str }
    """
    data = request.get_json() or {}
    skills = data.get("skills", "")
    if isinstance(skills, list):
        skills_str = " | ".join(skills[:3])
    else:
        skills_str = str(skills).replace(",", " | ") if skills else "AWS | Kubernetes | Python"

    headlines = [
        f"Cloud & DevOps Engineer | {skills_str} | Building Scalable, Zero-Downtime Infrastructure",
        f"Senior Software Engineer | {skills_str} | Driving High-Throughput Distributed Systems",
        f"Full-Stack Cloud Architect | {skills_str} | Transforming Monoliths into Agile Cloud Services",
        f"DevOps & SRE Specialist | {skills_str} | Automating CI/CD & Cutting Cloud Costs by 30%+"
    ]

    return jsonify({
        "headlines": headlines
    }), 200


@ai_bp.route("/optimize-keywords", methods=["POST"])
def optimize_keywords():
    """
    Analyzes resume text vs job description and suggests exact ATS keyword insertions.
    Input: { text: str, job_description: str }
    """
    data = request.get_json() or {}
    text = (data.get("text") or "").lower()
    jd = (data.get("job_description") or "").lower()

    if not jd:
        return jsonify({"message": "job_description is required"}), 400

    high_value_keywords = [
        "Kubernetes", "Docker", "Terraform", "AWS", "CI/CD", "Prometheus", "Grafana",
        "Microservices", "REST APIs", "Python", "Linux", "Infrastructure as Code",
        "Disaster Recovery", "Zero-Downtime Deployment", "Agile / Scrum"
    ]

    recommended = []
    for kw in high_value_keywords:
        if kw.lower() in jd and kw.lower() not in text:
            recommended.append(kw)

    if not recommended:
        recommended = ["Infrastructure as Code", "CI/CD Pipeline Automation", "Monitoring & Observability"]

    return jsonify({
        "recommended_keywords": recommended,
        "placement_suggestions": [
            f"Add '{recommended[0]}' under your Core Skills summary.",
            f"Incorporate '{recommended[1] if len(recommended) > 1 else 'Cloud Automation'}' in your most recent project description."
        ]
    }), 200


@ai_bp.route("/generate-achievement", methods=["POST"])
def generate_achievement():
    """
    Converts a generic work task into an impressive, quantifiable bullet point.
    Input: { role: str, task: str }
    """
    data = request.get_json() or {}
    task = (data.get("task") or "Managed cloud servers and fixed bugs").strip()
    role = (data.get("role") or "Software Engineer").strip()

    bullets = [
        f"Automated {task}, slashing incident MTTR (Mean Time to Resolution) by 42% and preventing 15+ potential production outages.",
        f"Redesigned the architecture for {task}, delivering a 3.5x throughput improvement while reducing infrastructure operational cost by $18,000 annually.",
        f"Spearheaded team-wide adoption of best practices for {task}, resulting in 99.98% service uptime across mission-critical services."
    ]

    return jsonify({
        "role": role,
        "original_task": task,
        "achievement_bullets": bullets
    }), 200
