import sqlite3
from pathlib import Path
import sys

def get_app_dir() -> Path:
    # If running as a PyInstaller EXE
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "data"
    # If running from source (python desktop.py)
    return Path(__file__).resolve().parent.parent / "data"

APP_DIR = get_app_dir()
DB_PATH = APP_DIR / "coach.db"


def connect():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def migrate():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS units (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT NOT NULL,
      title TEXT NOT NULL,
      pinned INTEGER NOT NULL DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS assessment_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      kind TEXT NOT NULL, -- Knowledge | Case Study | Project
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cards (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      event_kind TEXT NOT NULL, -- Knowledge | Case Study | Project
      prompt TEXT NOT NULL,
      answer TEXT NOT NULL,
      tags TEXT DEFAULT '',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      card_id INTEGER NOT NULL UNIQUE,
      due_date TEXT NOT NULL,
      interval_days INTEGER NOT NULL DEFAULT 1,
      ease REAL NOT NULL DEFAULT 2.5,
      last_grade INTEGER,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS labs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      event_kind TEXT NOT NULL, -- Case Study | Project (usually)
      title TEXT NOT NULL,
      goal TEXT NOT NULL,
      steps TEXT NOT NULL,
      verify TEXT NOT NULL,
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    # Settings (student name, number, etc.)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
    """)

    # AE2: items (tasks/questions) + responses
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ae2_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      code TEXT NOT NULL,          -- e.g. AE2-T1.1, AE2-Q2.3
      title TEXT NOT NULL,
      section TEXT NOT NULL,       -- Case Study | Research
      order_index INTEGER NOT NULL,
      template_md TEXT NOT NULL,
      word_guidance INTEGER,       -- optional
      UNIQUE(unit_id, code),
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ae2_responses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      item_code TEXT NOT NULL,
      content_md TEXT NOT NULL,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(unit_id, item_code),
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    # AE1: practice quiz bank + attempts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_questions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      q_type TEXT NOT NULL,        -- mcq
      question TEXT NOT NULL,
      choices_json TEXT NOT NULL,  -- JSON list of strings
      answer_index INTEGER NOT NULL,
      explanation TEXT NOT NULL,
      tags TEXT DEFAULT '',
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    # Ensure we have a 'context' column for quiz questions (short hints / term context)
    cur.execute("PRAGMA table_info(quiz_questions);")
    cols = [r[1] for r in cur.fetchall()]
    if 'context' not in cols:
        cur.execute("ALTER TABLE quiz_questions ADD COLUMN context TEXT DEFAULT '';")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      question_id INTEGER NOT NULL,
      chosen_index INTEGER NOT NULL,
      correct INTEGER NOT NULL,    -- 0/1
      ts TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE,
      FOREIGN KEY(question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
    );
    """)

    con.commit()
    con.close()
