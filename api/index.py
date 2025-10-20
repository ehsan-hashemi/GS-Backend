import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256
import jwt

from models.db import get_db, init_db
from services.auth import create_jwt, require_auth
from services.users import find_user_by_credentials, get_user_by_id
from services.announcements import create_announcement, list_announcements, delete_announcement
from services.news import create_news, list_news, get_live_news, set_live_news
from services.schedules import set_schedule, get_schedule_for_class
from services.reportcards import upload_reportcard, list_reportcards_for_student

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["JWT_EXPIRE_MINUTES"] = int(os.environ.get("JWT_EXPIRE_MINUTES", "120"))

# Initialize DB on cold start
init_db()

@app.route("/api/hello")
def hello():
    return {"msg": "Hello from Flask on Vercel!"}

# Health
@app.get("/api/health")
def health():
    return jsonify({"ok": True, "time": datetime.utcnow().isoformat()})

# Seed initial admin if not present
@app.post("/api/seed-admin")
def seed_admin():
    db = get_db()
    full_name = "مدیر گوهرتاج ۱۲۱"
    national_id = "1212121212"
    password = "65218"
    cur = db.execute("SELECT id FROM users WHERE national_id=?", (national_id,))
    if cur.fetchone():
        return jsonify({"created": False, "message": "Admin already exists"})
    pwd_hash = pbkdf2_sha256.hash(password)
    db.execute(
        "INSERT INTO users (full_name, national_id, password_hash, role) VALUES (?,?,?,?)",
        (full_name, national_id, pwd_hash, "admin"),
    )
    db.commit()
    return jsonify({"created": True, "admin_national_id": national_id})

# Login
@app.post("/api/login")
def login():
    data = request.get_json(force=True)
    full_name = data.get("full_name")
    national_id = data.get("national_id")
    password = data.get("password")
    user = find_user_by_credentials(full_name, national_id, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_jwt(app.config["SECRET_KEY"], user)
    return jsonify({"token": token, "role": user["role"]})

# Announcements (public list, admin manage)
@app.get("/api/announcements")
def announcements_list():
    return jsonify(list_announcements())

@app.post("/api/announcements")
@require_auth(roles=["admin"])
def announcements_create(user):
    data = request.get_json(force=True)
    return jsonify(create_announcement(user["id"], data)), 201

@app.delete("/api/announcements/<int:announcement_id>")
@require_auth(roles=["admin"])
def announcements_delete(user, announcement_id):
    ok = delete_announcement(announcement_id)
    return jsonify({"deleted": ok})

# News + live
@app.get("/api/news")
def news_list():
    return jsonify(list_news())

@app.get("/api/news/live")
def news_live():
    live = get_live_news()
    return jsonify(live or {})

@app.post("/api/news")
@require_auth(roles=["admin"])
def news_create(user):
    data = request.get_json(force=True)
    return jsonify(create_news(user["id"], data)), 201

@app.post("/api/news/live")
@require_auth(roles=["admin"])
def news_set_live(user):
    data = request.get_json(force=True)
    return jsonify(set_live_news(user["id"], data)), 200

# Users (admin adds admin/teacher/student)
@app.post("/api/users")
@require_auth(roles=["admin"])
def users_add(user):
    data = request.get_json(force=True)
    db = get_db()
    from passlib.hash import pbkdf2_sha256
    pwd_hash = pbkdf2_sha256.hash(data["password"])
    db.execute(
        "INSERT INTO users (full_name, national_id, password_hash, role, class_name, grade_level) VALUES (?,?,?,?,?,?)",
        (
            data["full_name"],
            data["national_id"],
            pwd_hash,
            data["role"],
            data.get("class_name"),
            data.get("grade_level"),
        ),
    )
    db.commit()
    return jsonify({"created": True}), 201

# Schedules
@app.post("/api/schedules")
@require_auth(roles=["admin"])
def schedules_set(user):
    data = request.get_json(force=True)
    return jsonify(set_schedule(data["class_name"], data["week_json"])), 200

@app.get("/api/schedules/<class_name>")
def schedules_get(class_name):
    sched = get_schedule_for_class(class_name)
    return jsonify(sched or {})

# Report cards
@app.post("/api/reportcards")
@require_auth(roles=["admin"])
def reportcards_upload(user):
    data = request.get_json(force=True)
    return jsonify(upload_reportcard(data["student_national_id"], data["term"], data["file_url"])), 201

@app.get("/api/reportcards/me")
@require_auth(roles=["student"])
def reportcards_list_me(user):
    return jsonify(list_reportcards_for_student(user["id"]))

# Student profile
@app.get("/api/me")
@require_auth(roles=["student", "admin", "teacher"])
def me(user):
    # Hide sensitive fields
    safe = {k: user[k] for k in ["id", "full_name", "national_id", "role", "class_name", "grade_level"]}
    return jsonify(safe)

# Default index
@app.get("/api/")
def root():
    return jsonify({"service": "Gohartaj School API"})