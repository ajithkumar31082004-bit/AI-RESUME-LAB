"""
AI RESUME LAB — Job Description Matching Routes
Matches candidate resumes against job specifications and calculates fit scores.
"""
from flask import Blueprint, request, jsonify, current_app

from models.database import db, Resume, JobDescription
from routes.auth import token_required
from routes.resume import get_optional_user
from services.ai_analyzer import analyze_resume, extract_skills

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/match", methods=["POST"])
def match_job():
    """
    Match a resume against a job description.
    Accepts: { resume_id: int (optional), resume_text: str (optional), job_description: str, title: str (optional), company: str (optional) }
    """
    data = request.get_json() or {}
    job_description = (data.get("job_description") or "").strip()
    resume_id = data.get("resume_id")
    resume_text = (data.get("resume_text") or "").strip()

    if not job_description:
        return jsonify({"message": "job_description is required"}), 400

    # Resolve resume text
    if resume_id:
        resume = db.session.get(Resume, resume_id)
        if resume and resume.resume_text:
            resume_text = resume.resume_text

    if not resume_text:
        return jsonify({"message": "Please provide either a valid resume_id or resume_text to match against."}), 400

    analysis = analyze_resume(resume_text, job_description)

    # Save to JobDescription if user is authenticated
    current_user = get_optional_user()
    job_id = None
    if current_user:
        jd_record = JobDescription(
            user_id=current_user.id,
            title=data.get("title") or "Target Position",
            company=data.get("company") or "Target Company",
            description=job_description,
            match_score=analysis.get("job_match", 75),
        )
        db.session.add(jd_record)
        db.session.commit()
        job_id = jd_record.id

    return jsonify({
        "job_id": job_id,
        "match_score": analysis.get("job_match", 75),
        "matching_skills": analysis.get("matching_skills", []),
        "missing_skills": analysis.get("missing_skills", []),
        "recommended_skills": analysis.get("missing_skills", [])[:5],
        "ats_score": analysis.get("ats_score"),
        "strengths": analysis.get("strengths", []),
        "weaknesses": analysis.get("weaknesses", []),
    }), 200


@jobs_bp.route("/list", methods=["GET"])
@token_required
def list_jobs(current_user):
    """List saved job descriptions and matches for current user."""
    jobs = JobDescription.query.filter_by(user_id=current_user.id).order_by(JobDescription.created_at.desc()).all()
    return jsonify({"jobs": [j.to_dict() for j in jobs]}), 200


@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@token_required
def delete_job(current_user, job_id):
    """Delete a saved job description."""
    job = JobDescription.query.filter_by(id=job_id, user_id=current_user.id).first()
    if not job:
        return jsonify({"message": "Job description not found"}), 404

    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job description deleted successfully"}), 200
