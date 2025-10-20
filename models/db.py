import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "/tmp/gohartaj.sqlite3")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      full_name TEXT NOT NULL,
      national_id TEXT NOT NULL UNIQUE,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('admin','teacher','student')),
      class_name TEXT,
      grade_level TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS announcements (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      body TEXT NOT NULL,
      published_at TEXT DEFAULT (datetime('now')),
      author_id INTEGER
    );
    CREATE TABLE IF NOT EXISTS news (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      body TEXT,
      is_live INTEGER DEFAULT 0,
      live_embed_code TEXT,
      published_at TEXT DEFAULT (datetime('now')),
      author_id INTEGER
    );
    CREATE TABLE IF NOT EXISTS schedules (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      class_name TEXT NOT NULL UNIQUE,
      week_json TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS reportcards (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      term INTEGER NOT NULL CHECK(term IN (1,2)),
      file_url TEXT NOT NULL,
      status TEXT DEFAULT 'published',
      created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    db.commit()