"""
AI RESUME LAB — Interview Preparation & Mock Sessions
Delivers targeted interview questions and evaluates user answers with AI feedback.
"""
from flask import Blueprint, request, jsonify
import re

from models.database import db, InterviewSession
from routes.auth import token_required
from routes.resume import get_optional_user

interview_bp = Blueprint("interview", __name__)

QUESTION_DATABASE = {
    "Cloud Engineer": {
        "technical": [
            "Explain the difference between containers and virtual machines. When would you use each?",
            "How does Kubernetes handle service discovery and load balancing?",
            "Describe the AWS shared responsibility model. Who is responsible for what?",
            "What is the difference between AWS EC2 Auto Scaling and Elastic Load Balancing (ELB)?",
            "How would you design a highly available, multi-region architecture on AWS?",
            "Explain how Terraform state management works and how to prevent state locking issues.",
            "What is the difference between blue-green and canary deployments?",
            "How does AWS IAM work? Explain roles, policies, and principal boundaries."
        ],
        "behavioral": [
            "Tell me about a time you had to troubleshoot a critical production outage under pressure.",
            "Describe a situation where you had to learn an unfamiliar cloud tool or framework quickly.",
            "How do you prioritize competing tasks when multiple high-severity incidents happen at once?",
            "Tell me about a time you modernized a CI/CD pipeline. What were the measurable outcomes?",
            "Describe a disagreement with a software architect or developer and how you reached consensus."
        ],
        "scenario": [
            "Your application's latency suddenly increases 10x at 2 AM. Walk me through your incident triage.",
            "A production deployment corrupted 15% of database rows. What immediate actions do you take?",
            "You need to migrate a monolithic backend to AWS microservices. How do you plan the transition?",
            "Your monthly AWS bill jumped by 250% unexpectedly. How do you pinpoint the culprit and remediate?"
        ],
        "hr": [
            "Why are you interested in this Cloud Engineering position?",
            "Where do you see yourself technically and professionally in three years?",
            "What is the most technically challenging infrastructure problem you have solved?",
            "How do you stay abreast of rapid advancements in cloud computing and DevOps?"
        ]
    },
    "DevOps Engineer": {
        "technical": [
            "Explain GitFlow versus trunk-based development. When is each best suited?",
            "How do you achieve zero-downtime rolling updates in Kubernetes?",
            "What is your strategy for instrumenting and collecting metrics in microservices?",
            "Compare Prometheus and Datadog in terms of architecture, cost, and maintenance.",
            "How does the Kubernetes Horizontal Pod Autoscaler determine when to scale?"
        ],
        "behavioral": [
            "Describe an automated workflow you built that significantly saved engineering hours.",
            "Tell me about your experience on an on-call rotation handling SLA breaches.",
            "How do you advocate for security and testing standards when deadlines are tight?"
        ],
        "scenario": [
            "Your test pipeline runtime grew from 5 minutes to 45 minutes. How do you optimize it?",
            "A rogue pod in production is consuming 100% CPU. How do you isolate and fix it?"
        ],
        "hr": [
            "What inspired you to specialize in DevOps and infrastructure engineering?",
            "How do you cultivate a healthy culture of blameless post-mortems?"
        ]
    },
    "Backend Developer": {
        "technical": [
            "Compare REST and GraphQL. Under what requirements would you choose GraphQL?",
            "Explain the N+1 query problem and how to prevent it with ORMs.",
            "How does database indexing work internally (e.g. B-Trees)? When are indexes detrimental?",
            "What is the CAP theorem and how does it influence your choice of distributed database?",
            "Explain caching strategies: Cache-Aside vs Write-Through vs Write-Back."
        ],
        "behavioral": [
            "Tell me about a complex database query or endpoint optimization you performed.",
            "Describe a time you discovered a critical bug in production code written by a peer."
        ],
        "scenario": [
            "Your service is receiving 15,000 write requests per second. How do you architect the ingestion layer?",
            "A legacy monolith has tight database coupling. How do you safely extract a new microservice?"
        ],
        "hr": [
            "What is your philosophy on writing clean, self-documenting code?",
            "What backend technology or framework are you most excited to learn next?"
        ]
    }
}


@interview_bp.route("/questions", methods=["POST"])
def get_questions():
    """Retrieve interview questions customized by role, level, and technology."""
    data = request.get_json() or {}
    role = data.get("role") or "Cloud Engineer"
    matched_role = "Cloud Engineer"
    for r in QUESTION_DATABASE:
        if r.lower() in role.lower() or role.lower() in r.lower():
            matched_role = r
            break

    questions = QUESTION_DATABASE[matched_role]
    return jsonify({
        "role": matched_role,
        "questions": questions
    }), 200


@interview_bp.route("/session", methods=["POST"])
def create_session():
    """Start a new interview session."""
    data = request.get_json() or {}
    role = data.get("role", "Cloud Engineer")
    level = data.get("level", "mid")

    current_user = get_optional_user()
    session_id = None
    if current_user:
        session = InterviewSession(
            user_id=current_user.id,
            role=role,
            level=level,
            score=0,
            questions_count=0,
            duration_seconds=0
        )
        db.session.add(session)
        db.session.commit()
        session_id = session.id

    return jsonify({
        "session_id": session_id or 1,
        "role": role,
        "level": level,
        "message": "Interview session started"
    }), 201


@interview_bp.route("/answer", methods=["POST"])
def evaluate_answer():
    """
    Evaluates candidate's answer based on STAR method, specificity, length, and metrics.
    Input: { session_id, question_id, answer, question_text (optional) }
    """
    data = request.get_json() or {}
    answer = (data.get("answer") or "").strip()

    if not answer:
        return jsonify({"message": "answer text is required"}), 400

    words = answer.split()
    word_count = len(words)
    has_numbers = bool(re.search(r"\d+", answer))
    has_star = bool(re.search(r"situation|task|action|result|impact|measure|outcome|reduced|increased", answer, re.IGNORECASE))
    has_tech_terms = bool(re.search(r"aws|docker|kubernetes|api|database|service|latency|pipeline|metric", answer, re.IGNORECASE))

    # Calculate rubric score (0-100)
    score = 45
    if word_count >= 50:
        score += 15
    if word_count >= 100:
        score += 10
    if has_numbers:
        score += 15
    if has_star:
        score += 10
    if has_tech_terms:
        score += 5

    score = min(98, score)

    # Formulate feedback tips
    tips = []
    if not has_numbers:
        tips.append("Add quantifiable metrics or percentage improvements (e.g., 'reduced deploy time by 30%').")
    if not has_star:
        tips.append("Structure behavioral answers using the STAR method (Situation, Task, Action, Result).")
    if word_count < 60:
        tips.append("Elaborate further; aim for 90–150 words to demonstrate depth of experience.")

    is_good = score >= 75
    feedback = {
        "score": score,
        "verdict": "Good Answer" if is_good else "Needs Improvement",
        "word_count": word_count,
        "has_metrics": has_numbers,
        "has_structure": has_star,
        "feedback_summary": "Strong, well-structured response with clear technical context." if is_good else "Answer is a good start, but needs more concrete details and metrics.",
        "tips": tips
    }

    # Update session in DB if available
    session_id = data.get("session_id")
    if session_id:
        try:
            sess = db.session.get(InterviewSession, session_id)
            if sess:
                current_answers = sess.answers
                current_answers.append({"answer": answer, "score": score})
                sess.answers = current_answers
                sess.score = int(round(sum(a["score"] for a in current_answers) / len(current_answers)))
                sess.questions_count = len(current_answers)
                db.session.commit()
        except Exception:
            db.session.rollback()

    return jsonify(feedback), 200


@interview_bp.route("/history", methods=["GET"])
@token_required
def get_history(current_user):
    """Retrieve user's past mock interview sessions."""
    sessions = InterviewSession.query.filter_by(user_id=current_user.id).order_by(InterviewSession.created_at.desc()).all()
    return jsonify({"sessions": [s.to_dict() for s in sessions]}), 200
