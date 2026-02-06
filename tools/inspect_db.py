import sqlite3
import json
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'data' / 'coach.db'
con = sqlite3.connect(p)
con.row_factory = sqlite3.Row
cur = con.cursor()
print('DB path:', p)
rows = cur.execute('select id, code, title from units').fetchall()
print('units:', [dict(r) for r in rows])
# show first quiz question for first unit
if rows:
    uid = rows[0]['id']
    q = cur.execute('select id, question, choices_json, context from quiz_questions where unit_id=? limit 1', (uid,)).fetchone()
    print('sample question:', dict(q) if q else None)
con.close()
