import json
from models.db import get_db

def set_schedule(class_name, week_json):
    db = get_db()
    data = json.dumps(week_json, ensure_ascii=False)
    db.execute("INSERT INTO schedules (class_name, week_json) VALUES (?,?) ON CONFLICT(class_name) DO UPDATE SET week_json=excluded.week_json, updated_at=datetime('now')", (class_name, data))
    db.commit()
    return {"updated": True}

def get_schedule_for_class(class_name):
    db = get_db()
    row = db.execute("SELECT week_json FROM schedules WHERE class_name=?", (class_name,)).fetchone()
    return json.loads(row["week_json"]) if row else None