from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, Response, JSONResponse, StreamingResponse
from datetime import date, timedelta
from io import BytesIO
import json
import random

from docx import Document

from app.db import migrate, connect
from app.seed import seed_all

app = FastAPI(title="Cert IV Coach (Offline)")

INDEX_HTML = r"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Cert IV Coach</title>
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <h2>Pinned Units</h2>
    <div id="units"></div>

    <div class="panel">
      <h3>Student details</h3>
      <label>Name</label>
      <input id="student_name" />
      <label>Student number (optional)</label>
      <input id="student_number" />
      <button onclick="saveSettings()">Save</button>
      <div class="muted" id="settingsSaved"></div>
    </div>
  </aside>

  <main class="main">
    <h1 id="unitTitle">Select a unit</h1>

    <section class="panel">
      <h3>Mode (flashcards)</h3>
      <div class="row">
        <button onclick="setMode('Knowledge')">Knowledge</button>
        <button onclick="setMode('Case Study')">Case Study</button>
        <button onclick="setMode('Project')">Project</button>
      </div>
      <div class="muted">Flashcards are optional; assessments below are the main thing for AE1/AE2.</div>
    </section>

    <section class="panel">
      <h3>Today's review</h3>
      <div id="review"></div>
    </section>

    <section class="panel">
      <h3>Assessment 1 (Practice Quiz)</h3>
      <div class="row">
        <button onclick="startQuiz()">Start / Next question</button>
        <button id="quizToggleContext" onclick="toggleQuizContext()" style="margin-left:8px;">Show hint</button>
      </div>
      <div class="card" id="quizBox" style="display:none;">
        <div id="quizQ" style="font-weight:600; margin-bottom:10px;"></div>
        <div id="quizContext" class="muted" style="margin-top:6px; display:none;"><strong>Hint:</strong> <span id="quizContextText"></span></div>
        <div id="quizChoices"></div>
        <div class="row" style="margin-top:10px;">
          <button onclick="submitQuiz()">Submit</button>
        </div>
        <div class="muted" id="quizFeedback" style="margin-top:10px;"></div>
      </div>
      <div class="muted" id="quizStats" style="margin-top:10px;"></div>
    </section>

    <section class="panel">
      <h3>Assessment 2 (Case Study Builder)</h3>
      <div class="muted">Pick a task/question, write your response, save, then export DOCX (one file per task).</div>

      <label>AE2 item</label>
      <select id="ae2ItemSelect" onchange="loadAE2Item()"></select>

      <label>Response (supports simple markdown tables using | pipes)</label>
      <textarea id="ae2Content" rows="14"></textarea>

      <div class="row">
        <button onclick="saveAE2()">Save</button>
        <button onclick="exportAE2()">Export DOCX</button>
      </div>

      <div class="muted" id="ae2Status"></div>
    </section>

    <section class="panel">
      <h3>Add a card (optional)</h3>
      <form id="cardForm">
        <input type="hidden" name="unit_id" id="card_unit_id" />
        <input type="hidden" name="event_kind" id="card_event_kind" value="Knowledge" />
        <label>Prompt</label>
        <textarea name="prompt" rows="2" required></textarea>
        <label>Answer</label>
        <textarea name="answer" rows="2" required></textarea>
        <label>Tags (comma)</label>
        <input name="tags" />
        <button type="submit">Add card</button>
      </form>
    </section>

  </main>
</div>

<!-- Glossary modal -->
<div id="glossaryModal" class="modal" style="display:none;">
  <div class="modal-overlay" onclick="closeGlossary()"></div>
  <div class="modal-content">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 id="glossaryTitle">Term</h3>
      <button class="modal-close" onclick="closeGlossary()">Close</button>
    </div>
    <div id="glossaryBody" style="margin-top:8px; white-space:pre-wrap;"></div>
  </div>
</div>

<script src="/app.js"></script>
</body>
</html>
"""

STYLES_CSS = r"""
body { font-family: system-ui, Segoe UI, Arial; margin:0; background:#0b0f17; color:#e7eefc; }
.layout { display:grid; grid-template-columns: 320px 1fr; height:100vh; }
.sidebar { padding:14px; border-right:1px solid #1b2a44; background:#070b12; overflow:auto; }
.main { padding:18px; overflow:auto; }
.unitBtn { width:100%; text-align:left; padding:10px; margin:6px 0; background:#0f1726; color:#e7eefc; border:1px solid #1b2a44; border-radius:10px; }
.panel { background:#0f1726; border:1px solid #1b2a44; border-radius:14px; padding:14px; margin:12px 0; }
textarea, input, select { width:100%; margin:6px 0 10px; padding:8px; border-radius:10px; border:1px solid #1b2a44; background:#0b1220; color:#e7eefc; }
button { padding:8px 12px; border-radius:10px; border:1px solid #2a3f66; background:#13213a; color:#e7eefc; cursor:pointer; }
.card { border:1px solid #223658; border-radius:12px; padding:10px; margin:10px 0; background:#0b1220; }
.row { display:flex; gap:10px; flex-wrap:wrap; }
.muted { opacity: 0.85; font-size: 0.95em; margin-top: 8px; }
/* Glossary modal */
.modal { position:fixed; inset:0; display:none; z-index:9999; }
.modal-overlay { position:absolute; inset:0; background:rgba(0,0,0,0.6); }
.modal-content { position:relative; width:520px; max-width:90%; margin:6% auto; background:#071022; border:1px solid #223658; padding:14px; border-radius:10px; color:#e7eefc; }
.modal-close { background:#112033; border:1px solid #223658; color:#e7eefc; padding:6px 10px; border-radius:8px; }
.glossary-term { color:#9bd0ff; text-decoration:underline; cursor:pointer; }
"""

APP_JS = r"""
let currentUnitId = null;
let currentMode = 'Knowledge';
let currentQuiz = null;

// Force default: hints hidden unless user clicks Show hint
if (!localStorage.getItem('quizShowContext')) {
  localStorage.setItem('quizShowContext', 'false');
}

async function api(path, options={}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || `HTTP ${res.status}`);
  }
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return await res.json();
  return await res.text();
}
async function refreshQuizStats() {
  if (!currentUnitId) return;

  const el = document.getElementById('quizStats');
  if (!el) return; // safety

  const s = await api(`/api/quiz/stats?unit_id=${currentUnitId}&window=20&tag_window=50`);

  let text = `Last ${s.window}: ${s.correct}/${s.total} (${s.pct}%)`;
  if (s.by_tag && s.by_tag.length) {
    const parts = s.by_tag.map(x => `${x.tag} ${x.pct}% (${x.correct}/${x.total})`);
    text += ` | Weak topics: ` + parts.join(', ');
  }
  el.textContent = text;
}

function setMode(mode) {
  currentMode = mode;
  document.getElementById('card_event_kind').value = mode;
  loadReview();
}

function unitButton(u) {
  const b = document.createElement('button');
  b.className = 'unitBtn';
  b.textContent = `${u.code} — ${u.title}`;
  b.onclick = () => selectUnit(u);
  return b;
}

async function loadUnits() {
  const data = await api('/api/units');
  const box = document.getElementById('units');
  box.innerHTML = '';
  data.units.forEach(u => box.appendChild(unitButton(u)));
}

async function selectUnit(u) {
  currentUnitId = u.id;
  document.getElementById('unitTitle').textContent = `${u.code} — ${u.title}`;
  document.getElementById('card_unit_id').value = u.id;
  await loadReview();
  await loadAE2Items();
  await loadSettings();
    await refreshQuizStats();
}

async function loadReview() {
  const box = document.getElementById('review');
  box.innerHTML = '';
  if (!currentUnitId) return;

  const data = await api(`/api/review/today?unit_id=${currentUnitId}&event_kind=${encodeURIComponent(currentMode)}`);
  if (data.cards.length === 0) {
    box.textContent = 'No cards due for this mode. Switch mode or add cards.';
    return;
  }

  data.cards.forEach(card => {
    const div = document.createElement('div');
    div.className = 'card';

    const p = document.createElement('div');
    p.textContent = card.prompt;

    const a = document.createElement('details');
    const sum = document.createElement('summary');
    sum.textContent = 'Show answer';
    const ans = document.createElement('div');
    ans.textContent = card.answer;
    a.appendChild(sum);
    a.appendChild(ans);

    const row = document.createElement('div');
    row.className = 'row';

    const grades = [
      {g:0, t:'Again'},
      {g:1, t:'Hard'},
      {g:2, t:'Good'},
      {g:3, t:'Easy'}
    ];

    grades.forEach(x => {
      const btn = document.createElement('button');
      btn.textContent = x.t;
      btn.onclick = async () => {
        const fd = new FormData();
        fd.append('card_id', card.id);
        fd.append('grade', x.g);
        await api('/api/review/grade', { method:'POST', body: fd });
        await loadReview();
      };
      row.appendChild(btn);
    });

    div.appendChild(p);
    div.appendChild(a);
    div.appendChild(row);
    box.appendChild(div);
  });
}

document.getElementById('cardForm').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (!currentUnitId) return alert('Select a unit first.');

  const fd = new FormData(ev.target);
  await api('/api/cards', { method:'POST', body: fd });
  ev.target.reset();
  document.getElementById('card_unit_id').value = currentUnitId;
  document.getElementById('card_event_kind').value = currentMode;
  await loadReview();
});

async function loadSettings() {
  const data = await api('/api/settings');
  document.getElementById('student_name').value = data.student_name || '';
  document.getElementById('student_number').value = data.student_number || '';
}

async function saveSettings() {
  const fd = new FormData();
  fd.append('student_name', document.getElementById('student_name').value);
  fd.append('student_number', document.getElementById('student_number').value);
  await api('/api/settings', { method:'POST', body: fd });
  document.getElementById('settingsSaved').textContent = 'Saved.';
  setTimeout(() => document.getElementById('settingsSaved').textContent = '', 1200);
}

async function startQuiz() {
  if (!currentUnitId) return alert('Select a unit first.');
  const data = await api(`/api/quiz/random?unit_id=${currentUnitId}`);
  currentQuiz = data;
  if (!currentQuiz || !currentQuiz.question_id) return alert('No quiz questions seeded for this unit yet.');

  document.getElementById('quizBox').style.display = 'block';
  document.getElementById('quizFeedback').textContent = '';
  document.getElementById('quizQ').textContent = currentQuiz.question;
    // show optional context hint (hidden by default; reveal via button)
    const ctxEl = document.getElementById('quizContext');
    const ctxTextEl = document.getElementById('quizContextText');
    const tb = document.getElementById('quizToggleContext');

    const hasCtx = !!(currentQuiz.context && currentQuiz.context.trim());

    quizHintVisible = false;
    ctxEl.style.display = 'none';
    ctxTextEl.innerHTML = hasCtx ? renderContext(currentQuiz.context) : '';

    if (tb) {
      tb.textContent = 'Show hint';
      tb.disabled = !hasCtx;
      tb.style.display = hasCtx ? 'inline-block' : 'none';
    }

  const box = document.getElementById('quizChoices');
  box.innerHTML = '';
  currentQuiz.choices.forEach((c, idx) => {
    const id = `q_${idx}`;
    const row = document.createElement('div');
    row.style.marginBottom = '6px';
    row.innerHTML = `<label><input type="radio" name="quizChoice" value="${idx}" id="${id}"> ${c}</label>`;
    box.appendChild(row);
  });
    await refreshQuizStats();
}

function saveQuizContextPref() {
  // deprecated: kept for backward compatibility with older saved prefs
}

function toggleQuizContext() {
  const tb = document.getElementById('quizToggleContext');
  const ctxEl = document.getElementById('quizContext');
  const ctxTextEl = document.getElementById('quizContextText');
  if (!tb || !ctxEl || !ctxTextEl) return;

  const hasCtx = !!(currentQuiz && currentQuiz.context && currentQuiz.context.trim());
  if (!hasCtx) return;

  quizHintVisible = !quizHintVisible;
  tb.textContent = quizHintVisible ? 'Hide hint' : 'Show hint';

  if (quizHintVisible) {
    ctxEl.style.display = 'block';
    ctxTextEl.innerHTML = renderContext(currentQuiz.context);
  } else {
    ctxEl.style.display = 'none';
  }
}

const GLOSSARY = {
  "SSH": "Secure Shell — a protocol for encrypted remote administration.",
  "Telnet": "An older remote terminal protocol that sends data in plaintext.",
  "firewall": "A system that filters network traffic according to rules.",
  "hash": "A fixed-size digest computed from data used to verify integrity.",
  "backup": "A copy of data kept so it can be restored after loss or damage.",
  "IDS": "Intrusion Detection System — monitors for suspicious activity and alerts.",
  "IPS": "Intrusion Prevention System — can detect and attempt to block attacks.",
  "MFA": "Multi-factor authentication — additional verification beyond a password.",
  "RAID": "A storage technology that provides redundancy but is not a substitute for backups."
};

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&');
}

function renderContext(text) {
  let out = text;
  Object.keys(GLOSSARY).forEach(term => {
    const re = new RegExp('\\b' + escapeRegExp(term) + '\\b', 'gi');
    out = out.replace(re, (match) => `<a href="#" class="glossary-term" data-term="${term}">${match}</a>`);
  });
  out = out.replace(/\n/g, '<br>');
  return out;
}

document.addEventListener('click', function(ev) {
  const a = ev.target.closest && ev.target.closest('.glossary-term');
  if (a) {
    ev.preventDefault();
    const term = a.getAttribute('data-term');
    openGlossary(term);
  }
});

function openGlossary(term) {
  const modal = document.getElementById('glossaryModal');
  const title = document.getElementById('glossaryTitle');
  const body = document.getElementById('glossaryBody');
  if (!modal) return;
  title.textContent = term;
  body.textContent = GLOSSARY[term] || 'Definition not found.';
  modal.style.display = 'block';
}

function closeGlossary() {
  const modal = document.getElementById('glossaryModal');
  if (modal) modal.style.display = 'none';
}

async function submitQuiz() {
  if (!currentQuiz) return;
  const chosen = document.querySelector('input[name="quizChoice"]:checked');
  if (!chosen) return alert('Pick an answer first.');

  const fd = new FormData();
  fd.append('unit_id', currentUnitId);
  fd.append('question_id', currentQuiz.question_id);
  fd.append('chosen_index', chosen.value);

  const data = await api('/api/quiz/answer', { method:'POST', body: fd });
  document.getElementById('quizFeedback').textContent = (data.correct ? 'Correct. ' : 'Not quite. ') + data.explanation;
    await refreshQuizStats();
}

async function loadAE2Items() {
  const sel = document.getElementById('ae2ItemSelect');
  sel.innerHTML = '';
  if (!currentUnitId) return;

  const data = await api(`/api/ae2/items?unit_id=${currentUnitId}`);
  data.items.forEach(it => {
    const opt = document.createElement('option');
    opt.value = it.code;
    opt.textContent = `${it.code} — ${it.title}`;
    sel.appendChild(opt);
  });

  if (data.items.length > 0) {
    sel.value = data.items[0].code;
    await loadAE2Item();
  }
}

async function loadAE2Item() {
  const code = document.getElementById('ae2ItemSelect').value;
  if (!currentUnitId || !code) return;

  const data = await api(`/api/ae2/item?unit_id=${currentUnitId}&item_code=${encodeURIComponent(code)}`);
  document.getElementById('ae2Content').value = data.content_md || data.template_md || '';
  document.getElementById('ae2Status').textContent = data.word_guidance ? `Word guidance: ~${data.word_guidance} words.` : '';
}

async function saveAE2() {
  const code = document.getElementById('ae2ItemSelect').value;
  const content = document.getElementById('ae2Content').value;

  const fd = new FormData();
  fd.append('unit_id', currentUnitId);
  fd.append('item_code', code);
  fd.append('content_md', content);

  await api('/api/ae2/response/save', { method:'POST', body: fd });
  document.getElementById('ae2Status').textContent = 'Saved.';
  setTimeout(() => loadAE2Item(), 200);
}

async function exportAE2() {
  const code = document.getElementById('ae2ItemSelect').value;
  const url = `/api/ae2/export_docx?unit_id=${currentUnitId}&item_code=${encodeURIComponent(code)}`;
  const res = await fetch(url);
  if (!res.ok) return alert('Export failed.');
  const blob = await res.blob();
  const cd = res.headers.get('content-disposition') || '';
  let filename = 'AE2.docx';
  const m = cd.match(/filename="([^"]+)"/);
  if (m) filename = m[1];

  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

loadUnits();
"""

@app.on_event("startup")
def startup():
    migrate()
    seed_all()

@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML

@app.get("/styles.css")
def styles():
    return Response(content=STYLES_CSS, media_type="text/css")

@app.get("/app.js")
def appjs():
    return Response(content=APP_JS, media_type="application/javascript")

@app.get("/api/settings")
def get_settings():
    con = connect()
    rows = con.execute("SELECT key, value FROM settings;").fetchall()
    con.close()
    kv = {r["key"]: r["value"] for r in rows}
    return {"student_name": kv.get("student_name", ""), "student_number": kv.get("student_number", "")}

@app.post("/api/settings")
def set_settings(student_name: str = Form(""), student_number: str = Form("")):
    con = connect()
    con.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", ("student_name", student_name.strip()))
    con.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", ("student_number", student_number.strip()))
    con.commit()
    con.close()
    return {"ok": True}

@app.get("/api/units")
def get_units():
    con = connect()
    rows = con.execute(
        "SELECT id, code, title, pinned FROM units ORDER BY pinned DESC, code ASC;"
    ).fetchall()
    con.close()
    return {"units": [dict(r) for r in rows]}

@app.post("/api/cards")
def create_card(
    unit_id: int = Form(...),
    event_kind: str = Form(...),
    prompt: str = Form(...),
    answer: str = Form(...),
    tags: str = Form("")
):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO cards (unit_id, event_kind, prompt, answer, tags) VALUES (?, ?, ?, ?, ?);",
        (unit_id, event_kind.strip(), prompt.strip(), answer.strip(), tags.strip())
    )
    card_id = cur.lastrowid
    cur.execute(
        "INSERT OR REPLACE INTO reviews (card_id, due_date, interval_days, ease) VALUES (?, ?, ?, ?);",
        (card_id, date.today().isoformat(), 1, 2.5)
    )
    con.commit()
    con.close()
    return {"ok": True, "card_id": card_id}

@app.get("/api/review/today")
def review_today(unit_id: int, event_kind: str):
    con = connect()
    rows = con.execute("""
        SELECT c.id, c.prompt, c.answer, c.tags, r.due_date, r.interval_days, r.ease
        FROM cards c
        JOIN reviews r ON r.card_id = c.id
        WHERE c.unit_id = ? AND c.event_kind = ? AND r.due_date <= ?
        ORDER BY r.due_date ASC
        LIMIT 30;
    """, (unit_id, event_kind, date.today().isoformat())).fetchall()
    con.close()
    return {"cards": [dict(r) for r in rows]}

def sm2_update(interval_days: int, ease: float, grade: int):
    if grade == 0:
        return 1, max(1.3, ease - 0.2)
    if grade == 1:
        return max(1, int(interval_days * 1.2)), max(1.3, ease - 0.15)
    if grade == 2:
        return max(1, int(interval_days * ease)), ease
    return max(1, int(interval_days * (ease + 0.3))), min(3.0, ease + 0.05)

@app.post("/api/review/grade")
def grade_card(card_id: int = Form(...), grade: int = Form(...)):
    from datetime import timedelta
    con = connect()
    row = con.execute("SELECT interval_days, ease FROM reviews WHERE card_id = ?;", (card_id,)).fetchone()
    if not row:
        con.close()
        return JSONResponse({"ok": False, "error": "No review row"}, status_code=404)

    new_interval, new_ease = sm2_update(int(row["interval_days"]), float(row["ease"]), int(grade))
    new_due = (date.today() + timedelta(days=new_interval)).isoformat()

    con.execute("""
      UPDATE reviews
      SET due_date = ?, interval_days = ?, ease = ?, last_grade = ?, updated_at = CURRENT_TIMESTAMP
      WHERE card_id = ?;
    """, (new_due, new_interval, new_ease, int(grade), card_id))
    con.commit()
    con.close()
    return {"ok": True, "next_due": new_due}

# -------------------------
# Quiz endpoints (AE1 practice)
# -------------------------
@app.get("/api/quiz/random")
def quiz_random(unit_id: int):
    con = connect()
    rows = con.execute("""
      SELECT id, question, choices_json, context
        FROM quiz_questions
        WHERE unit_id = ?
        ORDER BY RANDOM()
        LIMIT 1;
    """, (unit_id,)).fetchall()
    if not rows:
        con.close()
        return {"question_id": None}
    r = rows[0]
    con.close()
    return {"question_id": r["id"], "question": r["question"], "choices": json.loads(r["choices_json"]), "context": r["context"] or ""}

@app.post("/api/quiz/answer")
def quiz_answer(unit_id: int = Form(...), question_id: int = Form(...), chosen_index: int = Form(...)):
    con = connect()
    q = con.execute("""
        SELECT answer_index, explanation
        FROM quiz_questions
        WHERE id = ? AND unit_id = ?;
    """, (question_id, unit_id)).fetchone()
    if not q:
        con.close()
        return JSONResponse({"ok": False, "error": "Question not found"}, status_code=404)

    correct = 1 if int(chosen_index) == int(q["answer_index"]) else 0
    con.execute("""
        INSERT INTO quiz_attempts (unit_id, question_id, chosen_index, correct)
        VALUES (?, ?, ?, ?);
    """, (unit_id, question_id, int(chosen_index), correct))
    con.commit()
    con.close()
    return {"ok": True, "correct": bool(correct), "explanation": q["explanation"]}
@app.get("/api/quiz/stats")
def quiz_stats(unit_id: int, window: int = 20, tag_window: int = 50):
    con = connect()

    # Overall stats (last N attempts)
    rows = con.execute("""
        SELECT correct
        FROM quiz_attempts
        WHERE unit_id = ?
        ORDER BY ts DESC
        LIMIT ?;
    """, (unit_id, window)).fetchall()

    total = len(rows)
    correct_n = sum(int(r["correct"]) for r in rows) if rows else 0
    pct = round((correct_n / total) * 100, 1) if total else 0.0

    # Tag breakdown (last tag_window attempts)
    tag_rows = con.execute("""
        SELECT qa.correct, qq.tags
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qq.id = qa.question_id
        WHERE qa.unit_id = ?
        ORDER BY qa.ts DESC
        LIMIT ?;
    """, (unit_id, tag_window)).fetchall()

    tag_map = {}  # tag -> [correct_sum, total]
    for r in tag_rows:
        tags = (r["tags"] or "").split(",")
        tags = [t.strip() for t in tags if t.strip()]
        if not tags:
            tags = ["(untagged)"]
        for t in tags:
            if t not in tag_map:
                tag_map[t] = [0, 0]
            tag_map[t][0] += int(r["correct"])
            tag_map[t][1] += 1

    by_tag = []
    for tag, (c, n) in tag_map.items():
        by_tag.append({
            "tag": tag,
            "correct": c,
            "total": n,
            "pct": round((c / n) * 100, 1) if n else 0.0
        })

    # Sort weakest first, then by sample size desc
    by_tag.sort(key=lambda x: (x["pct"], -x["total"], x["tag"]))

    con.close()
    return {
        "window": window,
        "total": total,
        "correct": correct_n,
        "pct": pct,
        "by_tag": by_tag[:10]  # top 10 weakest tags
    }

# -------------------------
# AE2 endpoints (Case Study builder)
# -------------------------
@app.get("/api/ae2/items")
def ae2_items(unit_id: int):
    con = connect()
    rows = con.execute("""
        SELECT code, title, section, order_index
        FROM ae2_items
        WHERE unit_id = ?
        ORDER BY order_index ASC;
    """, (unit_id,)).fetchall()
    con.close()
    return {"items": [dict(r) for r in rows]}

@app.get("/api/ae2/item")
def ae2_item(unit_id: int, item_code: str):
    con = connect()
    item = con.execute("""
        SELECT code, title, section, template_md, word_guidance
        FROM ae2_items
        WHERE unit_id = ? AND code = ?;
    """, (unit_id, item_code)).fetchone()

    resp = con.execute("""
        SELECT content_md
        FROM ae2_responses
        WHERE unit_id = ? AND item_code = ?;
    """, (unit_id, item_code)).fetchone()

    con.close()
    if not item:
        return JSONResponse({"ok": False, "error": "Item not found"}, status_code=404)

    return {
        "code": item["code"],
        "title": item["title"],
        "section": item["section"],
        "template_md": item["template_md"],
        "word_guidance": item["word_guidance"],
        "content_md": resp["content_md"] if resp else ""
    }

@app.post("/api/ae2/response/save")
def ae2_save(unit_id: int = Form(...), item_code: str = Form(...), content_md: str = Form(...)):
    con = connect()
    con.execute("""
        INSERT OR REPLACE INTO ae2_responses (unit_id, item_code, content_md, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP);
    """, (unit_id, item_code.strip(), content_md))
    con.commit()
    con.close()
    return {"ok": True}

def _get_setting(con, key: str) -> str:
    r = con.execute("SELECT value FROM settings WHERE key = ?;", (key,)).fetchone()
    return r["value"] if r else ""

def _md_to_docx(document: Document, md: str):
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0

    def is_table_line(s: str) -> bool:
        s = s.strip()
        return s.startswith("|") and s.endswith("|") and s.count("|") >= 2

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        # Headings
        if line.startswith("#"):
            level = min(4, len(line) - len(line.lstrip("#")))
            text = line.lstrip("#").strip()
            document.add_heading(text, level=level)
            i += 1
            continue

        # Bullet
        if line.strip().startswith("- "):
            document.add_paragraph(line.strip()[2:].strip(), style="List Bullet")
            i += 1
            continue

        # Table (pipe markdown)
        if is_table_line(line) and i + 1 < len(lines) and ("---" in lines[i + 1]):
            table_lines = []
            while i < len(lines) and is_table_line(lines[i]):
                table_lines.append(lines[i].strip())
                i += 1

            rows = [[c.strip() for c in tl.strip("|").split("|")] for tl in table_lines]
            if len(rows) >= 2:
                header = rows[0]
                body = [r for r in rows[2:]]  # skip separator row

                cols = max(len(header), *(len(r) for r in body)) if body else len(header)
                t = document.add_table(rows=1 + len(body), cols=cols)
                t.style = "Table Grid"

                for c in range(cols):
                    t.cell(0, c).text = header[c] if c < len(header) else ""

                for r_idx, r in enumerate(body, start=1):
                    for c in range(cols):
                        t.cell(r_idx, c).text = r[c] if c < len(r) else ""

            continue

        # Paragraph (default)
        document.add_paragraph(line)
        i += 1

@app.get("/api/ae2/export_docx")
def ae2_export_docx(unit_id: int, item_code: str):
    con = connect()
    item = con.execute("""
        SELECT title, template_md
        FROM ae2_items
        WHERE unit_id = ? AND code = ?;
    """, (unit_id, item_code)).fetchone()

    resp = con.execute("""
        SELECT content_md
        FROM ae2_responses
        WHERE unit_id = ? AND item_code = ?;
    """, (unit_id, item_code)).fetchone()

    if not item:
        con.close()
        return JSONResponse({"ok": False, "error": "Item not found"}, status_code=404)

    student_name = _get_setting(con, "student_name") or "Student"
    student_number = _get_setting(con, "student_number") or ""
    con.close()

    content = (resp["content_md"] if resp else "").strip()
    if not content:
        content = item["template_md"]

    doc = Document()
    doc.add_heading("ICTNWK421/423 – Assessment Event 2 (Case Study)", level=1)
    doc.add_paragraph(f"Item: {item_code} — {item['title']}")
    doc.add_paragraph("")

    _md_to_docx(doc, content)

    # Footer text uses the first footer paragraph (python-docx model) [web:336][web:338]
    footer_text = student_name + (f" | {student_number}" if student_number else "")
    section = doc.sections[0]
    footer = section.footer
    if footer.paragraphs:
        footer.paragraphs[0].text = footer_text
    else:
        footer.add_paragraph(footer_text)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)

    safe_code = item_code.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filename = f"AE2_{safe_code}.docx"

    # Streaming download with proper content-disposition [web:341][web:350]
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )
