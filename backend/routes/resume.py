"""
AI RESUME LAB — Resume Routes
Handles resume upload, text extraction, analysis execution, and CRUD operations.
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from models.database import db, Resume, Analysis, JobDescription, User
from routes.auth import token_required, decode_token
from services.text_extractor import extract_resume_text
from services.s3_service import storage_service
from services.ai_analyzer import analyze_resume

resume_bp = Blueprint("resume", __name__)


def get_optional_user():
    """Extract user from Authorization header if present, otherwise None."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            data = decode_token(token)
            return User.query.get(data.get("user_id"))
        except Exception:
            return None
    return None


@resume_bp.route("/upload", methods=["POST"])
def upload_resume():
    """
    Upload resume file (PDF, DOCX, TXT), extract text, and run AI analysis.
    Works for both logged-in users and guest users.
    """
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded. Please select a file."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No file selected."}), 400

    allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "docx", "doc", "txt"})
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed_exts:
        return jsonify({"message": f"Unsupported file type .{ext}. Allowed types: {', '.join(allowed_exts)}"}), 400

    job_description = request.form.get("job_description", "").strip()
    current_user = get_optional_user()
    user_id = current_user.id if current_user else None

    try:
        # Save file to local/S3 storage
        stored = storage_service.save_file(file, user_id=user_id)

        # Extract text from saved local file
        resume_text = extract_resume_text(stored["file_path"], stored["original_filename"])

        if not resume_text or len(resume_text.strip()) < 30:
            resume_text = f"Resume document: {stored['original_filename']}. Content extracted automatically."

        # Run AI Analysis
        analysis_data = analyze_resume(resume_text, job_description)

        # If user is authenticated, persist to database
        resume_id = None
        if current_user:
            resume = Resume(
                user_id=current_user.id,
                filename=stored["filename"],
                original_filename=stored["original_filename"],
                file_path=stored["file_path"],
                s3_key=stored["s3_key"],
                s3_url=stored["s3_url"],
                file_size=stored["file_size"],
                file_type=stored["file_type"],
                resume_text=resume_text,
                ats_score=analysis_data.get("ats_score", 0),
            )
            db.session.add(resume)
            db.session.flush()

            resume_id = resume.id

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

            db.session.add(analysis)
            db.session.commit()

        # Build response payload
        response_payload = {
            "message": "Resume analyzed successfully",
            "resume_id": resume_id,
            "filename": stored["original_filename"],
            "s3_url": stored["s3_url"],
            **analysis_data
        }
        return jsonify(response_payload), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error analyzing uploaded resume: {e}", exc_info=True)
        return jsonify({"message": f"Failed to analyze resume: {str(e)}"}), 500


@resume_bp.route("/analyze-text", methods=["POST"])
def analyze_text():
    """Analyze raw resume text without file upload."""
    data = request.get_json() or {}
    resume_text = (data.get("resume_text") or "").strip()
    job_description = (data.get("job_description") or "").strip()

    if not resume_text:
        return jsonify({"message": "resume_text is required"}), 400

    if len(resume_text) < 50:
        return jsonify({"message": "Resume text is too short. Please provide at least 50 characters."}), 400

    analysis_data = analyze_resume(resume_text, job_description)

    current_user = get_optional_user()
    if current_user:
        try:
            resume = Resume(
                user_id=current_user.id,
                filename="pasted_resume.txt",
                original_filename="Pasted Resume",
                file_type="txt",
                resume_text=resume_text,
                ats_score=analysis_data.get("ats_score", 0),
            )
            db.session.add(resume)
            db.session.flush()

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

            db.session.add(analysis)
            db.session.commit()
            analysis_data["resume_id"] = resume.id
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f"Failed to persist pasted resume: {e}")

    return jsonify(analysis_data), 200


@resume_bp.route("/list", methods=["GET"])
@token_required
def list_resumes(current_user):
    """List all resumes belonging to current authenticated user."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return jsonify({"resumes": [r.to_dict() for r in resumes]}), 200


@resume_bp.route("/<int:resume_id>", methods=["GET"])
@token_required
def get_resume(current_user, resume_id):
    """Retrieve resume and latest analysis."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
    if not resume:
        return jsonify({"message": "Resume not found"}), 404

    latest_analysis = resume.analyses.order_by(Analysis.created_at.desc()).first()
    data = resume.to_dict()
    data["analysis"] = latest_analysis.to_dict() if latest_analysis else None
    return jsonify(data), 200


@resume_bp.route("/<int:resume_id>", methods=["DELETE"])
@token_required
def delete_resume(current_user, resume_id):
    """Delete a resume and its stored file."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
    if not resume:
        return jsonify({"message": "Resume not found"}), 404

    storage_service.delete_file(resume.s3_key, resume.file_path)
    db.session.delete(resume)
    db.session.commit()
    return jsonify({"message": "Resume deleted successfully"}), 200
