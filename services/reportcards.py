from models.db import get_db

def _find_student_by_nid(national_id):
    db = get_db()
    row = db.execute("SELECT id FROM users WHERE national_id=? AND role='student'", (national_id,)).fetchone()
    return row["id"] if row else None

def upload_reportcard(student_national_id, term, file_url):
    student_id = _find_student_by_nid(student_national_id)
    if not student_id:
        return {"error":"student not found"}
    db = get_db()
    db.execute("INSERT INTO reportcards (student_id, term, file_url) VALUES (?,?,?)",
               (student_id, int(term), file_url))
    db.commit()
    return {"created": True}

def list_reportcards_for_student(student_id):
    db = get_db()
    rows = db.execute("SELECT term, file_url, status, created_at FROM reportcards WHERE student_id=? ORDER BY term", (student_id,)).fetchall()
    return [dict(r) for r in rows]