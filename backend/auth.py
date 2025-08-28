from flask import Blueprint, request
import bcrypt
from .db import db
from .models import User

auth_bp = Blueprint("auth", __name__)

# Simple token-less session for local desktop use: client stores username after success.
# For production, use JWT/cookies. Here, keep it simple per project scope.
@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return {"error": "Username and password required"}, 400

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash):
        return {"error": "Invalid credentials"}, 401

    return {"user": user.to_dict()}
