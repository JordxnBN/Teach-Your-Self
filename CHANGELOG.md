# CertIVCoach — Changelog & Development Context

> This file documents all changes, patches, and architectural decisions so any
> LLM (or human) picking up this project has full context. Update this file
> every time you make a change.

---

## Architecture Overview

| Component | Technology | Notes |
|---|---|---|
| Backend | FastAPI (Python) | All routes in `app/server.py` |
| Frontend | Vanilla JS/HTML/CSS | Embedded as raw strings in `server.py` (`INDEX_HTML`, `STYLES_CSS`, `APP_JS`) |
| Database | SQLite | Schema in `app/db.py`, seeded by `app/seed.py` |
| Desktop wrapper | pywebview | `desktop.py` launches the app in a native window |
| AI grading | Google Gemini 2.0 Flash | Via `urllib.request` (no extra deps); key stored in `settings` table |

### Key files

- **`app/server.py`** (~3000 lines) — FastAPI app, all API endpoints, and the entire embedded frontend (HTML/CSS/JS as Python strings).
- **`app/db.py`** — SQLite schema with tables: `units`, `cards`, `reviews`, `quiz_questions`, `quiz_attempts`, `short_answer_questions`, `short_answer_attempts`, `daily_progress`, `assessment_events`, `ae2_items`, `settings`.
- **`app/seed.py`** — Seeds initial data: units, flashcards, MCQ questions (32/unit), short-answer questions (12/unit), AE2 case-study items.
- **`desktop.py`** — pywebview entry point.

---

## Change Log (newest first)

### 2026-02-07 — MCQ Shuffling, Double Submission Fix, UI Selection & PEP 8 Fixes

- **MCQ Answer Shuffling:** Implemented choice randomization in `APP_JS` to prevent students from memorizing answer positions. Correct indices are maintained for accurate scoring.
- **Double Submission Prevention:** Updated `submitQuiz` and `submitShortAnswer` to automatically advance to the next question if an answer has already been submitted, preventing duplicate tracking.
- **UI Enhancements:** Enabled text selection and standard context menus (autocorrect, etc.) in the `pywebview` window by setting `text_select=True` in `StudyCoach.py` and updating CSS.
- **PEP 8 Compliance:** Fixed multiple E302 style errors in `app/server.py` by ensuring two blank lines separate all top-level functions and decorators.
- **Learning Design (Plan):** Drafted plans for interleaved reviews, confidence-based transitions, and visual progress tracking.

### 2026-02-07 — Desktop polish, persistence, packaging, GitHub

- **Local UI persistence & polish:** `loadUnits()` now returns a promise so the saved `currentUnitId`, selected page/tab, flashcard mode, and mistake filter are restored from `localStorage` after units finish loading. `showPage`, `selectUnit`, `setMode`, and `setMistakeFilter` write back to `localStorage`, and new helpers like `toggleButtonLoading` plus clearer Gemini status messaging make the quiz/exam/clarify flows feel responsive.
- **Exam/quiz improvements:** Added “Ask about this question” buttons next to MCQ feedback, ensured challenge/clarify areas are reset per question, displayed Gemini clarification results with Markdown rendering, and guarded exam salt calls with stored answers so only answered questions hit Gemini between submissions.
- **Stronger SQLite persistence:** Database connections now use WAL mode with `PRAGMA synchronous = NORMAL`, migrations run through `_safe_alter()` wrappers, and every migration run performs a timestamped backup (`data/backups/`) before applying structural changes so old data can be restored safely.
- **Desktop/packaging overhaul:** Renamed `desktop.py` to `StudyCoach.py`, launched the app with a branded pywebview window (custom title, background, icon fallback), rewrote the PyInstaller spec/build script to output `dist/studycoachapp.exe`, and added `tools/create_icon.py` plus `build-studycoach.bat` to regenerate assets and rebuild easily. The new `.gitignore`/Black/Flake configs keep `build/`, `dist/`, and `data/` out of Git.
- **Project cleanup & GitHub:** Assets, docs (CONTEXT -> docs/CONTEXT.md, commit_commands -> docs/git-workflow.md), and helper scripts now live under `assets/`, `docs/`, and `tools/`. Redundant files and stale PyInstaller artifacts were removed, and the repository was pushed to `https://github.com/JordxnBN/Teach-Your-Self` with the updated history.

### 2026-02-08 — Exam Mode Persistence & Mistakes Tracking

- **Exam Mode Persistence:** Exam attempts (both MCQ and short answer) are now persisted to the database when the exam finishes, so they appear in the Mistakes tab and contribute to progress tracking.
- **Mistakes Source Tracking:** Added `source` column to `quiz_attempts` and `short_answer_attempts` tables to track where mistakes originated: "mcq_quiz", "short_answer", or "exam". The Mistakes tab now displays the source (formatted as "MCQ Quiz", "Short Answer", "Exam Mode") for each mistake.
- **Database Migration:** Added ALTER TABLE statements to add the `source` column to existing databases with appropriate defaults.

### 2026-02-09 — Challenge/Clarify Feedback Loop

- **Clarify everywhere:** Wrong answers in the Practice Quiz, Short Answer practice, and Exam review cards now include a “Challenge explanation” button. Clicking it opens a small textarea that asks the student to describe their confusion next to the flashcard/mistake notice (or replaces the exam review block when triggered).
- **Gemini-powered clarification API:** Added `_call_gemini_clarify()` plus the `POST /api/exam/challenge` endpoint that gathers the question text, correct answer, student response, and stored explanation, then prompts Gemini to “Explain why this answer is right” and returns a JSON object containing the clarification text (or error) for display.
- **Reused persistence:** Exam answers already insert into `quiz_attempts`/`short_answer_attempts` with a `source` tag, so the Clarify button uses that context (question ID/unit ID/answer text) and keeps mistakes/flashcards persistent across restarts while optionally creating a flashcard when the answer stays incorrect.
- **Reusable UI helpers:** Introduced shared JS/CSS helpers (`setChallengeTrigger`, `showChallengeUI`, `sendChallenge`, `launchExamChallenge`, and new `.challenge-area` styling) so the same flow works inside quiz/short-answer feedback or in the per-question exam review.

### 2026-02-08 — Proficiency Features (Question Bank + Exam + Explain)

- Expanded MCQ and short-answer banks to ~80 MCQs and ~30 short answers per unit, adding coverage for wireless security (WPA2/WPA3, 802.1X, rogue APs), VLANs/segmentation, PKI/certificates, incident response, data classification/DLP, and business continuity vs DRP. Seed versioning updated (`QUIZ_SEED_VERSION=3`, `SA_SEED_VERSION=1`) so existing databases automatically pick up the new content.
- Added a **Mistakes** panel and `GET /api/mistakes` endpoint to review all previously wrong questions (MCQ + SA), filter by tag, see your last answer vs the correct/model answer, and re-attempt them directly.
- Implemented **Exam Mode** (`/api/exam/start`, `/api/exam/answer`, `/api/exam/finish`) with a timed mock exam UI that pulls from the weighted question pool, tracks answers locally in memory, and shows a simple results review (score, time used, per-question correct/wrong with correct answers).
- Added **Explain-It-Back** mode with new `explain_topics` / `explain_attempts` tables, seed topics per unit, `GET /api/explain/random` and `POST /api/explain/check` endpoints that use Gemini (when configured) to rate student explanations 1–5 and give rubric-style feedback, plus a frontend panel where the student writes their own explanation and compares it to a model one.

### 2026-02-07 — Harder MCQ Distractors + Question Randomisation

**Problem:** Multiple-choice distractors were obviously wrong (e.g. "Improving Wi-Fi speed", "On the printer", "Digging physical tunnels"). Students could always eliminate 3/4 options without knowing the material.

**Changes:**

#### `app/seed.py`
- **Rewrote all 57 MCQ distractor sets** (7 shared + 25 ICTNWK421 + 25 ICTNWK423) with plausible, technically-related alternatives that require genuine understanding to eliminate. Design principles for new distractors:
  - Use correct terminology from the field (not absurd/joke answers)
  - Represent common student misconceptions (e.g. confusing RPO with RTO)
  - Be similar in length and detail to the correct answer
  - Describe real concepts, just not the one being asked about
- **Added `QUIZ_SEED_VERSION` mechanism** — a version string (`"2"`) stored in the `settings` table. When bumped, it forces re-seed of quiz questions on next app start (deletes old questions + re-inserts). This ensures users get the updated distractors without manually deleting their database.

#### `app/server.py`
- **Fixed deterministic question ordering** — Both `/api/quiz/random` and `/api/short-answer/random` previously used `ORDER BY last_seen ASC LIMIT 10` which always returned the same 10 candidates in the same order on each app restart. Now:
  - Fetches ALL questions for the unit (no `LIMIT 10`)
  - Applies `random.shuffle(candidates)` before passing to `_weighted_pick`
  - `_weighted_pick` still uses weakness-weighted `random.choices` so weak areas are still prioritised, but the pool is randomised first

**How the re-seed version works:**
1. `seed.py` reads `settings.quiz_seed_version` from DB
2. If it doesn't match `QUIZ_SEED_VERSION` constant (or doesn't exist), it deletes all quiz questions for each unit and re-inserts them
3. After seeding, it writes the current version to settings so it doesn't re-trigger

---

### 2026-02-06 — Learning Efficiency Features (Batch)

Five features implemented in a single session:

#### 1. Weak Area Targeting
- **`_get_tag_weakness(con, attempts_table, questions_table, unit_id, score_col)`** — Calculates per-tag weakness scores from attempt history.
- **`_weighted_pick(candidates, tag_weakness)`** — Selects questions weighted by tag weakness; unseen questions get highest priority (weight=10.0).
- Both `/api/quiz/random` and `/api/short-answer/random` now use these helpers instead of pure random selection.

#### 2. Progress Dashboard
- New `<section class="panel">` for "Progress Dashboard" in the HTML.
- **`GET /api/progress`** endpoint — Aggregates `quiz_attempts` and `short_answer_attempts` into daily stats (correct, total, streak, overall_pct) for the last N days.
- **`loadProgress()`** JS function — Renders bar charts and streak counter.

#### 3. Auto-Generate Flashcards from Mistakes
- **`_maybe_create_card(con, unit_id, prompt, answer, tags)`** — Creates a flashcard (type "Knowledge", tags "auto") when a question is answered incorrectly, if one doesn't already exist for that prompt.
- Called from `quiz_answer()`, `sa_check()`, `sa_self_grade()`, and `sa_teach()`.
- Frontend shows a "Flashcard created" notification when `card_created` is true.

#### 4. Expanded Glossary / Clickable Terms
- **`GLOSSARY` object** in JS expanded from ~9 to 50+ terms covering protocols, security concepts, cryptography, backup/recovery, attacks, standards, and general networking.
- **`renderContext(text)`** JS function highlights glossary terms as clickable links across quiz questions, choices, short-answer questions, feedback, and hints.
- Clicking a term shows an alert with its definition.

#### 5. "I Don't Know — Teach Me" Button
- New button in the Short Answer panel.
- **`teachMeSA()`** JS function — Disables input, calls `/api/short-answer/teach`.
- **`POST /api/short-answer/teach`** endpoint — Calls `_call_gemini_teach()` for a teaching explanation, records a score=0 attempt, auto-creates a flashcard.
- **`_call_gemini_teach(api_key, question, model_answer)`** — Separate Gemini prompt optimised for teaching (plain text, not JSON). Falls back to stored explanation if API fails.

---

### 2026-02-06 — Short Answer Quiz Panel + Gemini Integration

#### `app/db.py`
- Added `short_answer_questions` table (id, unit_id, question, model_answer, explanation, tags, context).
- Added `short_answer_attempts` table (id, unit_id, question_id, student_answer, score 0/1/2, ai_feedback, ts).
- Added `daily_progress` table for progress tracking.

#### `app/seed.py`
- Seeded 24 short-answer questions (12 per unit) with model answers, explanations, tags, and context hints.

#### `app/server.py`
- **Short Answer endpoints:**
  - `GET /api/short-answer/random` — Returns a random question (now with weak-area weighting).
  - `POST /api/short-answer/check` — Grades via Gemini AI; falls back to self-grading.
  - `POST /api/short-answer/self-grade` — Manual grading when AI unavailable.
  - `GET /api/short-answer/stats` — Returns attempt counts and score distribution.
- **Gemini integration:**
  - `_call_gemini(api_key, prompt)` — Calls Gemini 2.0 Flash via `urllib.request`. Uses `ssl.create_default_context()` with fallback to unverified context for Windows compatibility. Includes retry logic for HTTP 429 (rate limit) with exponential backoff (up to 3 retries, 4s/8s waits).
  - `POST /api/settings/gemini-key` — Save API key to settings table.
  - `GET /api/settings/gemini-key-status` — Check if key is configured.
  - `GET /api/settings/gemini-key-test` — Diagnostic endpoint to test key.
- **Frontend:** New Short Answer panel with question display, textarea, submit/next buttons, feedback area, self-grading fallback, and stats bar.

---

### Bugs Fixed

| Date | Bug | Root Cause | Fix |
|---|---|---|---|
| 2026-02-06 | "No API key set" even after saving key | SSL certificate verification failing on Windows; generic error message hiding real issue | Added `ssl` context handling with fallback; improved error reporting to show `ai_error` detail |
| 2026-02-06 | "AI grading failed: AI grading failed: HTTP Error 429" (double prefix) | `_call_gemini` returned "AI grading failed: HTTP 429..." and caller prepended it again | Fixed `_call_gemini` to return only the specific error; added retry logic for 429 with exponential backoff |
| 2026-02-07 | Same question order every app restart | SQL `ORDER BY last_seen ASC LIMIT 10` was deterministic | Removed LIMIT, fetch all questions, `random.shuffle()` before weighted pick |

---

## Conventions & Notes for Future LLMs

1. **Single-file frontend:** All HTML/CSS/JS lives in `server.py` as Python string constants. Don't create separate `.html`/`.css`/`.js` files.
2. **No extra dependencies:** The app uses only Python stdlib + FastAPI + uvicorn + pywebview. Gemini calls use `urllib.request`, not `requests` or `httpx`.
3. **Seed versioning:** When changing seed data (questions, cards), bump `QUIZ_SEED_VERSION` (or add a similar mechanism for SA questions) to force re-seed on existing databases.
4. **Quiz question format:** `mcq(question, [4 choices], answer_index, explanation, tags, context)`. The `answer_index` is 0-based.
5. **Distractor quality:** All wrong answers should be plausible, use real terminology, and represent common misconceptions. Never use joke/absurd options.
6. **Database migrations:** `db.py` uses `CREATE TABLE IF NOT EXISTS` — add new tables there. For column additions to existing tables, use `ALTER TABLE` with try/except.
7. **Error handling pattern:** API endpoints return `{"ai_error": "message"}` when AI calls fail; frontend checks this field and displays it.
8. **Rate limiting:** Gemini free tier allows 15 req/min. The retry logic handles 429s automatically.
