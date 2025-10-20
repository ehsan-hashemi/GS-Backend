from models.db import get_db

def list_announcements():
    db = get_db()
    rows = db.execute("SELECT * FROM announcements ORDER BY published_at DESC").fetchall()
    return [dict(r) for r in rows]

def create_announcement(author_id, data):
    db = get_db()
    db.execute("INSERT INTO announcements (title, body, author_id) VALUES (?,?,?)",
               (data["title"], data["body"], author_id))
    db.commit()
    return {"created": True}

def delete_announcement(announcement_id):
    db = get_db()
    db.execute("DELETE FROM announcements WHERE id=?", (announcement_id,))
    db.commit()
    return True