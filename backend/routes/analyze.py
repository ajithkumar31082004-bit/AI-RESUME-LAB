"""
AI RESUME LAB — Analysis Routes
Fetches and re-runs detailed resume analysis reports.
"""
from flask import Blueprint, request, jsonify, current_app

from models.database import db, Resume, Analysis
from routes.auth import token_required
from services.ai_analyzer import analyze_resume

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/<int:resume_id>", methods=["GET"])
@token_required
def get_analysis(current_user, resume_id):
    """Retrieve analysis results for a specific resume."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
    if not resume:
        return jsonify({"message": "Resume not found"}), 404

    analysis = resume.analyses.order_by(Analysis.created_at.desc()).first()
    if not analysis:
        # If no analysis exists yet, run it on the fly
        if resume.resume_text:
            data = analyze_resume(resume.resume_text)
            analysis = Analysis(
                resume_id=resume.id,
                ats_score=data.get("ats_score"),
                job_match_score=data.get("job_match"),
                structure_score=data.get("resume_structure"),
                keywords_score=data.get("keywords_score"),
                skills_score=data.get("skills_score"),
                experience_score=data.get("experience_score"),
                education_score=data.get("education_score"),
                formatting_score=data.get("formatting_score"),
            )
            analysis.strengths = data.get("strengths", [])
            analysis.weaknesses = data.get("weaknesses", [])
            analysis.recommendations = data.get("recommendations", [])
            analysis.missing_skills = data.get("missing_skills", [])
            analysis.matching_skills = data.get("matching_skills", [])
            db.session.add(analysis)
            db.session.commit()
        else:
            return jsonify({"message": "No analysis available for this resume"}), 404

    return jsonify(analysis.to_dict()), 200


@analyze_bp.route("/<int:resume_id>/reanalyze", methods=["POST"])
@token_required
def reanalyze_resume(current_user, resume_id):
    """Re-analyze an existing resume against a new job description."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
    if not resume:
        return jsonify({"message": "Resume not found"}), 404

    if not resume.resume_text:
        return jsonify({"message": "Resume has no extracted text to analyze"}), 400

    data = request.get_json() or {}
    job_description = data.get("job_description", "").strip()

    analysis_data = analyze_resume(resume.resume_text, job_description)

    # Save new analysis record
    analysis = Analysis(
        resume_id=resume.id,
        ats_score=analysis_data.get("ats_score"),
        job_match_score=analysis_data.get("job_match"),
        structure_score=analysis_data.get("resume_structure"),
        keywords_score=analysis_data.get("keywords_score"),
        skills_score=analysis_data.get("skills_score"),
        experience_score=analysis_data.get("experience_score"),
        education_score=analysis_data.get("education_score"),
        formatting_score=analysis_data.get("formatting_score"),
    )
    analysis.strengths = analysis_data.get("strengths", [])
    analysis.weaknesses = analysis_data.get("weaknesses", [])
    analysis.recommendations = analysis_data.get("recommendations", [])
    analysis.missing_skills = analysis_data.get("missing_skills", [])
    analysis.matching_skills = analysis_data.get("matching_skills", [])

    # Update resume ATS score
    resume.ats_score = analysis_data.get("ats_score")

    db.session.add(analysis)
    db.session.commit()

    return jsonify({
        "message": "Resume re-analyzed successfully",
        **analysis_data
    }), 200
