import sqlite3
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'data' / 'coach.db'
con = sqlite3.connect(p)
cur = con.cursor()

mappings = {
    "What does the principle of least privilege mean?": "Limit accounts to only the permissions they need to perform their job.",
    "Which is the best description of a firewall’s main job?": "A device or software that filters network traffic according to allow/deny rules.",
    "Why is SSH preferred over Telnet for remote administration?": "SSH encrypts terminal sessions; Telnet sends data unencrypted over the network.",
    "What is a hash primarily used for?": "A hash produces a fixed-size digest used to verify data integrity — any change alters the hash.",
    "Which backup approach best supports fast recovery from accidental deletion for end users?": "Keep versioned backups or file history so users can restore prior versions quickly.",
    "What is an IDS designed to do?": "An Intrusion Detection System monitors for suspicious activity and raises alerts.",
    "Which is a reasonable way to improve password security in an organisation?": "Enforce minimum strength, complexity, and lockout policies to reduce brute-force attacks.",
}

for q, ctx in mappings.items():
    cur.execute("UPDATE quiz_questions SET context=? WHERE question=?", (ctx, q))
    print('Updated', cur.rowcount, 'rows for', q)

con.commit()
con.close()
print('Done')
