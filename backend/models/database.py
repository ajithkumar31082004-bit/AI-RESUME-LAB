"""
AI RESUME LAB — Database Models
SQLAlchemy ORM models with relationships.
Architecture is ready for PostgreSQL/MySQL migration.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

def utc_now():
    return datetime.now(timezone.utc)

db = SQLAlchemy()


class User(db.Model):
    """User account model."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(512), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    resumes = db.relationship("Resume", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    job_descriptions = db.relationship("JobDescription", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    applications = db.relationship("Application", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    interview_sessions = db.relationship("InterviewSession", backref="owner", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_private=False):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return data

    def __repr__(self):
        return f"<User {self.email}>"


class Resume(db.Model):
    """Uploaded resume storage model."""
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(512))       # Local path
    s3_key = db.Column(db.String(512))           # S3 object key
    s3_url = db.Column(db.String(512))           # S3 public/presigned URL
    file_size = db.Column(db.Integer)            # Bytes
    file_type = db.Column(db.String(20))         # pdf, docx, txt
    resume_text = db.Column(db.Text)             # Extracted text
    ats_score = db.Column(db.Integer)            # 0-100
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    analyses = db.relationship("Analysis", backref="resume", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.original_filename or self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "ats_score": self.ats_score,
            "s3_url": self.s3_url,
            "is_primary": self.is_primary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class JobDescription(db.Model):
    """Job description model for matching."""
    __tablename__ = "job_descriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    match_score = db.Column(db.Integer)          # 0-100
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "match_score": self.match_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Analysis(db.Model):
    """Resume analysis results model."""
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, index=True)
    job_description_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id"))

    # Scores (0-100)
    ats_score = db.Column(db.Integer)
    job_match_score = db.Column(db.Integer)
    structure_score = db.Column(db.Integer)
    keywords_score = db.Column(db.Integer)
    skills_score = db.Column(db.Integer)
    experience_score = db.Column(db.Integer)
    education_score = db.Column(db.Integer)
    formatting_score = db.Column(db.Integer)

    # JSON-encoded lists
    _strengths = db.Column("strengths", db.Text)
    _weaknesses = db.Column("weaknesses", db.Text)
    _recommendations = db.Column("recommendations", db.Text)
    _missing_skills = db.Column("missing_skills", db.Text)
    _matching_skills = db.Column("matching_skills", db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)

    # Property helpers for JSON fields
    @property
    def strengths(self):
        return json.loads(self._strengths or "[]")

    @strengths.setter
    def strengths(self, val):
        self._strengths = json.dumps(val)

    @property
    def weaknesses(self):
        return json.loads(self._weaknesses or "[]")

    @weaknesses.setter
    def weaknesses(self, val):
        self._weaknesses = json.dumps(val)

    @property
    def recommendations(self):
        return json.loads(self._recommendations or "[]")

    @recommendations.setter
    def recommendations(self, val):
        self._recommendations = json.dumps(val)

    @property
    def missing_skills(self):
        return json.loads(self._missing_skills or "[]")

    @missing_skills.setter
    def missing_skills(self, val):
        self._missing_skills = json.dumps(val)

    @property
    def matching_skills(self):
        return json.loads(self._matching_skills or "[]")

    @matching_skills.setter
    def matching_skills(self, val):
        self._matching_skills = json.dumps(val)

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "ats_score": self.ats_score,
            "job_match": self.job_match_score,
            "resume_structure": self.structure_score,
            "keywords_score": self.keywords_score,
            "skills_score": self.skills_score,
            "experience_score": self.experience_score,
            "education_score": self.education_score,
            "formatting_score": self.formatting_score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "missing_skills": self.missing_skills,
            "matching_skills": self.matching_skills,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Application(db.Model):
    """Job application tracker model."""
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_url = db.Column(db.String(512))
    status = db.Column(db.String(50), default="applied")  # applied, interview, offer, rejected
    notes = db.Column(db.Text)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    applied_date = db.Column(db.Date)
    interview_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "job_title": self.job_title,
            "job_url": self.job_url,
            "status": self.status,
            "notes": self.notes,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "interview_date": self.interview_date.isoformat() if self.interview_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class InterviewSession(db.Model):
    """Mock interview session model."""
    __tablename__ = "interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(100))
    level = db.Column(db.String(50))
    score = db.Column(db.Integer)            # 0-100 overall score
    questions_count = db.Column(db.Integer)
    _answers = db.Column("answers", db.Text)  # JSON
    duration_seconds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)

    @property
    def answers(self):
        return json.loads(self._answers or "[]")

    @answers.setter
    def answers(self, val):
        self._answers = json.dumps(val)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "level": self.level,
            "score": self.score,
            "questions_count": self.questions_count,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
