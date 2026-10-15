"""
AI RESUME LAB — Configuration
Loads settings from environment variables with sensible defaults.
NEVER commit .env files or actual secrets to version control.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Core ────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production-use-long-random-string")
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    TESTING = False

    # ── Database ────────────────────────────────────────────────
    # Development: SQLite
    # Production: Set DATABASE_URL to postgresql://user:pass@host/db
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db', 'resume_lab.db')}"
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # ── JWT ─────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ── File Upload ─────────────────────────────────────────────
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}

    # ── AWS S3 ──────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "")
    S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL", "")

    # ── AI / LLM ────────────────────────────────────────────────
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o-mini")
    AI_MAX_TOKENS = int(os.environ.get("AI_MAX_TOKENS", "2048"))
    AI_TEMPERATURE = float(os.environ.get("AI_TEMPERATURE", "0.7"))

    # ── CORS ────────────────────────────────────────────────────
    ALLOWED_ORIGINS = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")

    # ── Rate Limiting ────────────────────────────────────────────
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "100 per hour")
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "memory://")

    # ── Email (optional) ─────────────────────────────────────────
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set to True to log SQL queries


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Override to use PostgreSQL in production:
    # SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
