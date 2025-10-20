from models.db import get_db

def list_news():
    db = get_db()
    rows = db.execute("SELECT * FROM news WHERE is_live=0 ORDER BY published_at DESC").fetchall()
    return [dict(r) for r in rows]

def get_live_news():
    db = get_db()
    row = db.execute("SELECT * FROM news WHERE is_live=1 ORDER BY published_at DESC LIMIT 1").fetchone()
    return dict(row) if row else None

def create_news(author_id, data):
    db = get_db()
    db.execute("INSERT INTO news (title, body, is_live, live_embed_code, author_id) VALUES (?,?,?,?,?)",
               (data.get("title"), data.get("body"), 0, data.get("live_embed_code"), author_id))
    db.commit()
    return {"created": True}

def set_live_news(author_id, data):
    db = get_db()
    # mark previous live as non-live
    db.execute("UPDATE news SET is_live=0 WHERE is_live=1")
    db.execute("INSERT INTO news (title, body, is_live, live_embed_code, author_id) VALUES (?,?,?,?,?)",
               (data.get("title","پخش زنده"), data.get("body"), 1, data.get("live_embed_code"), author_id))
    db.commit()
    return {"live_set": True}