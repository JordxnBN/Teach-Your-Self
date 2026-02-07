import shutil
import sqlite3
from datetime import datetime
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
BACKUP_DIR = APP_DIR / "backups"

def _column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table});")
    return any(r[1] == column for r in cur.fetchall())

def _safe_alter(cur, ddl, description):
    try:
        cur.execute(ddl)
    except sqlite3.OperationalError as exc:
        print(f"Skipped migration ({description}): {exc}")

def backup_database():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = BACKUP_DIR / f"coach-{timestamp}.db"
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def connect():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA journal_mode = WAL;")
    con.execute("PRAGMA synchronous = NORMAL;")
    return con

def migrate():
    backup_path = backup_database()
    if backup_path:
        print(f"Backed up database before migration: {backup_path}")
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
    if not _column_exists(cur, "quiz_questions", "context"):
        _safe_alter(cur, "ALTER TABLE quiz_questions ADD COLUMN context TEXT DEFAULT '';", "quiz_questions.context")

    # Ensure we have a 'source' column for quiz_attempts
    if not _column_exists(cur, "quiz_attempts", "source"):
        _safe_alter(
            cur,
            "ALTER TABLE quiz_attempts ADD COLUMN source TEXT NOT NULL DEFAULT 'mcq_quiz';",
            "quiz_attempts.source",
        )

    # Ensure we have a 'source' column for short_answer_attempts
    if not _column_exists(cur, "short_answer_attempts", "source"):
        _safe_alter(
            cur,
            "ALTER TABLE short_answer_attempts ADD COLUMN source TEXT NOT NULL DEFAULT 'short_answer';",
            "short_answer_attempts.source",
        )

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      question_id INTEGER NOT NULL,
      chosen_index INTEGER NOT NULL,
      correct INTEGER NOT NULL,    -- 0/1
      source TEXT NOT NULL DEFAULT 'mcq_quiz',  -- 'mcq_quiz' or 'exam'
      ts TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE,
      FOREIGN KEY(question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
    );
    """)

    # Short answer quiz bank + attempts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS short_answer_questions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      question TEXT NOT NULL,
      model_answer TEXT NOT NULL,
      explanation TEXT NOT NULL,
      tags TEXT DEFAULT '',
      context TEXT DEFAULT '',
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS short_answer_attempts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      question_id INTEGER NOT NULL,
      student_answer TEXT NOT NULL,
      score INTEGER NOT NULL,       -- 0=incorrect, 1=partial, 2=correct
      ai_feedback TEXT DEFAULT '',
      source TEXT NOT NULL DEFAULT 'short_answer',  -- 'short_answer' or 'exam'
      ts TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE,
      FOREIGN KEY(question_id) REFERENCES short_answer_questions(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_progress (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      dt TEXT NOT NULL,
      quiz_correct INTEGER NOT NULL DEFAULT 0,
      quiz_total INTEGER NOT NULL DEFAULT 0,
      sa_correct INTEGER NOT NULL DEFAULT 0,
      sa_total INTEGER NOT NULL DEFAULT 0,
      UNIQUE(unit_id, dt),
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_served_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      question_id INTEGER NOT NULL,
      served_ts TEXT NOT NULL,
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    # Explain-it-back topics and attempts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS explain_topics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      topic_prompt TEXT NOT NULL,
      model_explanation TEXT NOT NULL,
      tags TEXT DEFAULT '',
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS explain_attempts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      unit_id INTEGER NOT NULL,
      topic_id INTEGER NOT NULL,
      student_text TEXT NOT NULL,
      ai_score INTEGER NOT NULL,     -- 1-5 rating
      ai_feedback TEXT DEFAULT '',
      ts TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE,
      FOREIGN KEY(topic_id) REFERENCES explain_topics(id) ON DELETE CASCADE
    );
    """)

    con.commit()
    con.close()
