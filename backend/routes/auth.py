"""
AI RESUME LAB — Auth Routes
JWT-based authentication with password hashing.
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
import re

from models.database import db, User

auth_bp = Blueprint("auth", __name__)


# ── JWT Helpers ────────────────────────────────────────────────
def generate_token(user_id: int) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "user_id": user_id,
        "exp": now + datetime.timedelta(hours=24),
        "iat": now,
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])


def token_required(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        if not token:
            return jsonify({"message": "Authentication token is missing"}), 401

        try:
            data = decode_token(token)
            current_user = db.session.get(User, data["user_id"])
            if not current_user or not current_user.is_active:
                return jsonify({"message": "Invalid or expired token"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


# ── Validation Helpers ─────────────────────────────────────────
def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, ""


# ── Routes ─────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # Validation
    if not name:
        return jsonify({"message": "Name is required"}), 400
    if not email or not validate_email(email):
        return jsonify({"message": "Valid email is required"}), 400
    valid_pw, pw_msg = validate_password(password)
    if not valid_pw:
        return jsonify({"message": pw_msg}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "An account with this email already exists"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        "message": "Account created successfully",
        "token": token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"message": "Account is disabled. Please contact support."}), 403

    token = generate_token(user.id)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict(),
    })


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user):
    """Logout (JWT is stateless; client must discard the token)."""
    return jsonify({"message": "Logged out successfully"})


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get current user profile."""
    return jsonify({"user": current_user.to_dict()})


@auth_bp.route("/password", methods=["PUT"])
@token_required
def change_password(current_user):
    """Change user password."""
    data = request.get_json() or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not check_password_hash(current_user.password_hash, old_password):
        return jsonify({"message": "Current password is incorrect"}), 400

    valid_pw, pw_msg = validate_password(new_password)
    if not valid_pw:
        return jsonify({"message": pw_msg}), 400

    current_user.password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
    db.session.commit()
    return jsonify({"message": "Password changed successfully"})
