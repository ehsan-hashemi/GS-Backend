import os
from functools import wraps
from flask import request, jsonify
import jwt
from models.db import get_db

def create_jwt(secret, user):
    payload = {"sub": user["id"], "role": user["role"]}
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def get_user_by_id(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None

def require_auth(roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization","")
            if not auth.startswith("Bearer "):
                return jsonify({"error":"Unauthorized"}), 401
            token = auth.split(" ",1)[1]
            try:
                payload = jwt.decode(token, os.environ.get("SECRET_KEY","dev-secret"), algorithms=["HS256"])
            except Exception:
                return jsonify({"error":"Invalid token"}), 401
            user = get_user_by_id(payload.get("sub"))
            if not user:
                return jsonify({"error":"User not found"}), 404
            if roles and user["role"] not in roles:
                return jsonify({"error":"Forbidden"}), 403
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator