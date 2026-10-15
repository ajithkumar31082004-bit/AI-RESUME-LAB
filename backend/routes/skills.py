"""
AI RESUME LAB — Skill Gap & Learning Path Routes
Analyzes skill gaps against industry roles and delivers tailored roadmaps.
"""
from flask import Blueprint, request, jsonify

skills_bp = Blueprint("skills", __name__)

ROLE_SKILL_REQUIREMENTS = {
    "cloud_engineer": {
        "title": "Cloud Engineer",
        "skills": [
            "Linux", "Networking", "Python", "AWS", "Docker",
            "Terraform", "Kubernetes", "CI/CD", "Bash", "Prometheus", "Git"
        ],
        "roadmap": [
            {"label": "Linux", "icon": "🐧", "status": "completed", "desc": "Master Linux fundamentals, shell scripting, file systems"},
            {"label": "Networking", "icon": "🌐", "status": "completed", "desc": "TCP/IP, DNS, HTTP, VPNs, firewalls"},
            {"label": "Python", "icon": "🐍", "status": "completed", "desc": "Scripting, automation, Boto3 for AWS"},
            {"label": "AWS Core", "icon": "☁️", "status": "current", "desc": "EC2, S3, VPC, IAM, RDS, Lambda"},
            {"label": "Docker", "icon": "🐳", "status": "locked", "desc": "Containers, Dockerfile, Docker Compose"},
            {"label": "Terraform", "icon": "⚙️", "status": "locked", "desc": "Infrastructure as Code, state management"},
            {"label": "Kubernetes", "icon": "☸️", "status": "locked", "desc": "Orchestration, Helm, EKS, service mesh"},
            {"label": "CI/CD", "icon": "🔄", "status": "locked", "desc": "Jenkins, GitHub Actions, ArgoCD"}
        ]
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "skills": [
            "Linux", "Git", "Docker", "Kubernetes", "CI/CD",
            "Prometheus", "Grafana", "Terraform", "Ansible", "Python"
        ],
        "roadmap": [
            {"label": "Linux", "icon": "🐧", "status": "completed", "desc": "OS fundamentals, scripting, package management"},
            {"label": "Git", "icon": "📝", "status": "completed", "desc": "Version control, branching, GitFlow"},
            {"label": "Docker", "icon": "🐳", "status": "completed", "desc": "Containerization, multi-stage builds"},
            {"label": "Kubernetes", "icon": "☸️", "status": "current", "desc": "Pod management, services, Ingress, RBAC"},
            {"label": "CI/CD", "icon": "🔄", "status": "locked", "desc": "Jenkins, GitHub Actions, pipeline as code"},
            {"label": "Monitoring", "icon": "📊", "status": "locked", "desc": "Prometheus, Grafana, ELK Stack"},
            {"label": "Terraform", "icon": "⚙️", "status": "locked", "desc": "IaC, modules, workspaces, state"},
            {"label": "Security", "icon": "🔒", "status": "locked", "desc": "DevSecOps, SAST, DAST, secrets management"}
        ]
    },
    "backend_developer": {
        "title": "Backend Developer",
        "skills": [
            "Python", "REST APIs", "SQL", "PostgreSQL", "Redis",
            "Docker", "System Design", "Microservices", "Git", "Kafka"
        ],
        "roadmap": [
            {"label": "Python/Java", "icon": "💻", "status": "completed", "desc": "Strong OOP, design patterns, SOLID principles"},
            {"label": "REST APIs", "icon": "🔌", "status": "completed", "desc": "HTTP methods, status codes, API design"},
            {"label": "Databases", "icon": "🗄️", "status": "completed", "desc": "SQL, indexing, transactions, ORM"},
            {"label": "Caching", "icon": "⚡", "status": "current", "desc": "Redis, Memcached, cache strategies"},
            {"label": "Message Queues", "icon": "📨", "status": "locked", "desc": "RabbitMQ, Kafka, async processing"},
            {"label": "Microservices", "icon": "🔧", "status": "locked", "desc": "Service decomposition, API Gateway"},
            {"label": "Docker/K8s", "icon": "🐳", "status": "locked", "desc": "Containerize and deploy services"},
            {"label": "System Design", "icon": "🏗️", "status": "locked", "desc": "Scalability, CAP theorem, distributed systems"}
        ]
    },
    "data_scientist": {
        "title": "Data Scientist",
        "skills": [
            "Python", "SQL", "Machine Learning", "Pandas", "NumPy",
            "Scikit-Learn", "Deep Learning", "PyTorch", "Data Analysis", "NLP"
        ],
        "roadmap": [
            {"label": "Python", "icon": "🐍", "status": "completed", "desc": "NumPy, Pandas, Matplotlib, Scikit-learn"},
            {"label": "Statistics", "icon": "📊", "status": "completed", "desc": "Probability, hypothesis testing, regression"},
            {"label": "ML Basics", "icon": "🤖", "status": "current", "desc": "Supervised, unsupervised, model evaluation"},
            {"label": "Deep Learning", "icon": "🧠", "status": "locked", "desc": "TensorFlow, PyTorch, neural networks"},
            {"label": "NLP", "icon": "💬", "status": "locked", "desc": "Text processing, transformers, BERT"},
            {"label": "Big Data", "icon": "📦", "status": "locked", "desc": "Spark, Hadoop, data pipelines"},
            {"label": "MLOps", "icon": "⚙️", "status": "locked", "desc": "Model deployment, monitoring, MLflow"}
        ]
    }
}


@skills_bp.route("/gap", methods=["POST"])
def analyze_skill_gap():
    """
    Analyzes gap between user skills and benchmark role competencies.
    Input: { skills: list[str] or comma-separated str, target_role: str }
    """
    data = request.get_json() or {}
    raw_skills = data.get("skills", [])
    if isinstance(raw_skills, str):
        user_skills = [s.strip().lower() for s in raw_skills.split(",") if s.strip()]
    else:
        user_skills = [str(s).strip().lower() for s in raw_skills if str(s).strip()]

    target_role_key = (data.get("target_role") or "cloud_engineer").lower().replace(" ", "_").replace("-", "_")
    role_info = ROLE_SKILL_REQUIREMENTS.get(target_role_key, ROLE_SKILL_REQUIREMENTS["cloud_engineer"])
    req_skills = role_info["skills"]

    # Match skills
    matching = []
    missing = []
    for req in req_skills:
        req_clean = req.lower()
        if any(req_clean in u or u in req_clean for u in user_skills):
            matching.append(req)
        else:
            missing.append(req)

    # Score calculation
    total = len(req_skills)
    match_ratio = len(matching) / total if total > 0 else 0
    score = int(round(35 + match_ratio * 60))

    return jsonify({
        "target_role": target_role_key,
        "role_name": role_info["title"],
        "match_score": score,
        "matching_skills": matching,
        "missing_skills": missing,
        "recommended_skills": missing[:5],
        "roadmap": role_info["roadmap"],
    }), 200


@skills_bp.route("/learning-path", methods=["GET"])
def get_learning_path():
    """Returns curated learning roadmap for specified target role."""
    role_key = request.args.get("role", "cloud_engineer").lower().replace(" ", "_").replace("-", "_")
    role_info = ROLE_SKILL_REQUIREMENTS.get(role_key, ROLE_SKILL_REQUIREMENTS["cloud_engineer"])

    return jsonify({
        "role": role_key,
        "role_name": role_info["title"],
        "steps": role_info["roadmap"],
        "core_skills": role_info["skills"],
    }), 200
