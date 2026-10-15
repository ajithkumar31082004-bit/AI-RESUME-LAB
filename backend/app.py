"""
AI RESUME LAB — Flask Backend Application
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from models.database import db
from routes.auth import auth_bp
from routes.resume import resume_bp
from routes.analyze import analyze_bp
from routes.jobs import jobs_bp
from routes.skills import skills_bp
from routes.interview import interview_bp
from routes.dashboard import dashboard_bp
from routes.ai_content import ai_bp
import logging


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Initialize extensions ──────────────────────────────────
    db.init_app(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config["ALLOWED_ORIGINS"],
            "supports_credentials": True,
        }
    })

    # ── Register blueprints ────────────────────────────────────
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    app.register_blueprint(analyze_bp, url_prefix="/api/analyze")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(skills_bp, url_prefix="/api/skills")
    app.register_blueprint(interview_bp, url_prefix="/api/interview")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # ── Ensure directories exist ───────────────────────────────
    import os
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        sqlite_path = db_uri.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(sqlite_path)), exist_ok=True)
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    # ── Create tables ──────────────────────────────────────────
    with app.app_context():
        db.create_all()
        logging.info("Database tables created.")

    # ── Health check ───────────────────────────────────────────
    @app.route("/health")
    def health():
        return {"status": "ok", "version": "1.0.0", "service": "AI Resume Lab API"}

    @app.errorhandler(404)
    def not_found(e):
        return {"message": "Resource not found", "error": str(e)}, 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return {"message": "Method not allowed", "error": str(e)}, 405

    @app.errorhandler(500)
    def server_error(e):
        logging.error(f"Server error: {e}")
        return {"message": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
