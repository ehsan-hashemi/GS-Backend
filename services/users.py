from models.db import get_db
from passlib.hash import pbkdf2_sha256

def find_user_by_credentials(full_name, national_id, password):
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE full_name=? AND national_id=?", (full_name, national_id)
    ).fetchone()
    if not row:
        return None
    user = dict(row)
    if not pbkdf2_sha256.verify(password, user["password_hash"]):
        return None
    return user

def get_user_by_id(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None