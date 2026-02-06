import json
from app.db import connect

STUDENT_NAME_DEFAULT = "Jordan Barron"

def seed_all():
    con = connect()
    cur = con.cursor()

    units = [
        ("ICTNWK421", "Install, configure and test network security", 1),
        ("ICTNWK423", "Manage network and data integrity", 1),
        ("WORKPLACE", "Cluster: ICT Analysis (426/404/432)", 0),
    ]

    cur.execute("SELECT COUNT(*) AS n FROM units;")
    if cur.fetchone()["n"] == 0:
        cur.executemany("INSERT INTO units (code, title, pinned) VALUES (?, ?, ?);", units)

        urows = cur.execute("SELECT id, code FROM units;").fetchall()
        uid = {r["code"]: r["id"] for r in urows}

        events = []
        for code in ("ICTNWK421", "ICTNWK423"):
            events += [
                (uid[code], "Assessment event 1", "Knowledge"),
                (uid[code], "Assessment event 2", "Case Study"),
                (uid[code], "Assessment event 3", "Project"),
            ]
        cur.executemany(
            "INSERT INTO assessment_events (unit_id, name, kind) VALUES (?, ?, ?);",
            events
        )

        # Starter cards (keep your existing idea)
        cards = [
            (uid["ICTNWK421"], "Knowledge", "Define least privilege. Give 2 network examples.", "Least privilege means only the minimum access required. Examples: restrict admin access to management VLAN only; allow only required ports to servers; role-based accounts on devices.", "security,principles"),
            (uid["ICTNWK421"], "Knowledge", "Stateful vs stateless firewall: what’s the difference?", "Stateful tracks connection state and allows return traffic automatically; stateless evaluates each packet independently against rules.", "firewall"),
            (uid["ICTNWK421"], "Knowledge", "What does 'default deny' mean and why use it?", "Block by default, allow only explicitly required traffic; reduces attack surface and mistakes.", "policy"),
            (uid["ICTNWK423"], "Knowledge", "Define data integrity and give 3 controls that support it.", "Integrity means data is accurate and not improperly changed. Controls: hashing/checksums, access control/least privilege, audit logging/change control, backups + restore testing.", "integrity,controls"),
            (uid["ICTNWK423"], "Knowledge", "Hashing vs encryption: what does each provide?", "Hashing supports integrity verification (detect change). Encryption provides confidentiality (and with authentication can support integrity).", "crypto"),
            (uid["ICTNWK423"], "Knowledge", "What is restore testing and why is it mandatory?", "Regularly restoring from backups to confirm backups are usable and meet RPO/RTO; otherwise backups might be corrupt or incomplete.", "backup"),
        ]
        cur.executemany(
            "INSERT INTO cards (unit_id, event_kind, prompt, answer, tags) VALUES (?, ?, ?, ?, ?);",
            cards
        )

    # Ensure student name exists in settings
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);", ("student_name", STUDENT_NAME_DEFAULT))
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);", ("student_number", ""))

    # Seed AE2 items (idempotent)
    uid_row = cur.execute("SELECT id FROM units WHERE code = 'ICTNWK421';").fetchone()
    if uid_row:
        unit_id = int(uid_row["id"])

        cur.execute("SELECT COUNT(*) AS n FROM ae2_items WHERE unit_id = ?;", (unit_id,))
        if cur.fetchone()["n"] == 0:
            items = []

            def add(code, title, section, order_index, template_md, word_guidance=None):
                items.append((unit_id, code, title, section, order_index, template_md.strip() + "\n", word_guidance))

            # Part 1: Case study tasks (paraphrased structure to match what the doc asks for)
            add("AE2-T1.1", "Task 1.1 – Org structure + link to integrity/security", "Case Study", 10, """
Write ~75 words.

- Organisation structure (teams/roles, reporting lines).
- Main business functions (what they do day-to-day).
- How structure/functions affect data integrity + security (controls, approvals, access, responsibilities).

Answer:
""", 75)

            add("AE2-T1.2", "Task 1.2 – Recommend 2 current networking technologies", "Case Study", 20, """
Write ~150 words (point form allowed).

For each technology:
- Features/capabilities (security-relevant).
- Example use at Millennium Media (where/why).
- How it supports security requirements.

Tech 1:
Tech 2:
""", 150)

            add("AE2-T1.3-1", "Task 1.3 (1) – Privacy legislation + guideline", "Case Study", 30, """
Fill the table (about ~60 words each row).

| Privacy Legislation/Guideline | Description | How it relates to MM security requirements |
|---|---|---|
|  |  |  |
|  |  |  |

""", 120)

            add("AE2-T1.3-2", "Task 1.3 (2) – Two privacy issues", "Case Study", 31, """
Fill the table (~75 words per issue).

| Privacy issue | Description | How it relates to integrity/security requirements |
|---|---|---|
|  |  |  |
|  |  |  |

""", 150)

            add("AE2-T1.4", "Task 1.4 – Two reliable security info sources", "Case Study", 40, """
Fill the table (~50 words per source). Include URL.

| Security source (name + URL) | What it provides | How it supports MM network security needs |
|---|---|---|
|  |  |  |
|  |  |  |

""", 100)

            add("AE2-T1.5", "Task 1.5 – 4 environmental threats (Penrith) + risk analysis", "Case Study", 50, """
Research local environmental threats relevant to data security and complete:

| Item | Threat | Potential damage | Likelihood (Low/Med/High + why) |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |

""", 200)

            add("AE2-T1.6", "Task 1.6 – Two protection systems/controls for environmental threats", "Case Study", 60, """
Pick two threats from Task 1.5 and complete:

| Item | Threat | System/Controls | Explanation (how it protects data) |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |

""", 120)

            add("AE2-T1.7", "Task 1.7 – Two backup types + plan + backup/restore + rollback overview", "Case Study", 70, """
Complete each part (point form ok, ~50 words each).

a) Two backup types (name + short description):
b) Recommendation plan (solution, type, schedule, location):
c) Procedure overview: backup + restore:
d) Procedure overview: rollback to earlier state:

Answer:
""", 200)

            add("AE2-T1.8", "Task 1.8 – Identify threats/vulns by asset category + prioritise", "Case Study", 80, """
Provide 2 threats/vulns for each category, explain why they could exist, then prioritise 1–4 with reasoning.

| Asset category | Threats & vulnerabilities (2 + short why) | Priority (1–4) + why |
|---|---|---|
| Network |  |  |
| Software |  |  |
| Hardware |  |  |
| User access |  |  |

""", 200)

            add("AE2-T1.9", "Task 1.9 – Two network performance monitoring tools + compatibility", "Case Study", 90, """
Include tool + URL (if applicable) and explain compatibility.

| Tool identification | Explanation of compatibility with MM network |
|---|---|
|  |  |
|  |  |

""", 100)

            # Part 2: Research questions (key ones you’ll answer in tables)
            add("AE2-Q2.1", "Q2.1 – Tools: monitoring, hashing/encryption, backup/disaster recovery", "Research", 110, """
Fill the table (~50–100 words each row).

| Function | Software product name + vendor | Overview of features/capabilities |
|---|---|---|
| Manage/monitor medium–large network |  |  |
| Hashing or encryption (integrity/confidentiality) |  |  |
| Backup/disaster recovery |  |  |

References (paste URLs):
- 
- 
""")

            add("AE2-Q2.2", "Q2.2 – Secure remote access: SSH vs Telnet + SSH encryption standards", "Research", 120, """
a) SSH vs Telnet (purpose + comparison):
b) SSH encryption standards (overview: what’s used and why it’s secure):

Answer:

References (paste URLs):
- 
""")

            add("AE2-Q2.3", "Q2.3 – HTTPS, DNS, DHCP (purpose + functionality)", "Research", 130, """
| Protocol | Description (20–40 words) |
|---|---|
| HTTPS |  |
| DNS |  |
| DHCP |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.4", "Q2.4 – Eavesdropping, interception, corruption, falsification", "Research", 140, """
| Threat | Description (~50 words) |
|---|---|
| Eavesdropping |  |
| Data interception |  |
| Data corruption |  |
| Data falsification |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.5", "Q2.5 – Firewall roles/procedures across LAN/WLAN/WAN/DMZ/TCP/IP/app protocols", "Research", 150, """
| Area | Firewall security systems/procedures (brief) |
|---|---|
| LAN |  |
| WLAN |  |
| WAN |  |
| DMZ |  |
| TCP |  |
| IP |  |
| App protocols (e.g. HTTP/FTP) |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.6", "Q2.6 – Security perimeter + enterprise perimeter hardware (incl firewall)", "Research", 160, """
a) Define security perimeter + functions (about ~100 words):
b) Two enterprise perimeter hardware products + features/capabilities (include a hardware firewall):

Answer:

References (paste URLs):
- 
""")

            add("AE2-Q2.7", "Q2.7 – VPN concepts (encryption, firewall considerations, tunnelling, auth)", "Research", 170, """
| VPN concept | Description |
|---|---|
| Data encryption |  |
| Firewall considerations |  |
| Packet tunnelling |  |
| Authentication process |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.8", "Q2.8 – VPN types: site-to-site, client-to-site, extranet", "Research", 180, """
| VPN type | Description |
|---|---|
| Site-to-site |  |
| Client-to-site (user-to-site) |  |
| Extranet |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.9", "Q2.9 – Two antivirus solutions + scanning techniques (screenshots if relevant)", "Research", 190, """
| Item | Solution | Techniques (how to scan + what to check) |
|---|---|---|
| 1 |  |  |
| 2 |  |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.10", "Q2.10 – Tools/procedures: auditing, IDS, penetration testing", "Research", 200, """
| Function | Product name | Procedure summary (how you’d use it) |
|---|---|---|
| Network access auditing |  |  |
| Intrusion detection |  |  |
| Penetration testing |  |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.11", "Q2.11 – Three monitoring/security tools (features + 2 capabilities)", "Research", 210, """
| Tool | General features | 2 functions/capabilities |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

References (paste URLs):
- 
""")

            add("AE2-Q2.12", "Q2.12 – Demonstrate backup + restore (systems/procedures)", "Research", 220, """
| Item | Systems and procedures (~50 words each) |
|---|---|
| Backup |  |
| Restore |  |

References (paste URLs):
- 
""")

            cur.executemany("""
                INSERT INTO ae2_items (unit_id, code, title, section, order_index, template_md, word_guidance)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, items)

    # Seed quiz questions (idempotent: only if empty)
    for ucode in ("ICTNWK421", "ICTNWK423"):
        u = cur.execute("SELECT id FROM units WHERE code = ?;", (ucode,)).fetchone()
        if not u:
            continue
        unit_id = int(u["id"])

        cur.execute("SELECT COUNT(*) AS n FROM quiz_questions WHERE unit_id = ?;", (unit_id,))
        if cur.fetchone()["n"] > 0:
            continue

        qs = []
        def mcq(question, choices, answer_index, explanation, tags="", context=""):
            qs.append((unit_id, "mcq", question.strip(), json.dumps(choices), int(answer_index), explanation.strip(), tags, context.strip()))

        # A solid starter pack (we can expand to 100+ later)
        mcq(
            "What does the principle of least privilege mean?",
            ["Give users admin rights so they can work faster", "Give only the minimum access needed to do the job", "Block all access by default forever", "Allow access based on seniority only"],
            1,
            "Least privilege means users/services get only the permissions required for their tasks, reducing impact if an account is compromised.",
            "principles",
            "Limit accounts to only the permissions they need to perform their job."
        )
        mcq(
            "Which is the best description of a firewall’s main job?",
            ["Encrypt all files on a computer", "Filter network traffic according to rules/policy", "Physically secure the server room", "Replace antivirus software"],
            1,
            "Firewalls enforce traffic policy at boundaries (and sometimes internally) by allowing/denying traffic based on rules.",
            "firewall",
            "A device or software that filters network traffic according to allow/deny rules."
        )
        mcq(
            "Why is SSH preferred over Telnet for remote administration?",
            ["SSH is faster for large files", "SSH encrypts the session; Telnet is plaintext", "Telnet supports MFA by default", "Telnet uses stronger ciphers than SSH"],
            1,
            "SSH provides encrypted remote access; Telnet sends credentials and commands in plaintext.",
            "ssh,telnet",
            "SSH encrypts terminal sessions; Telnet sends data unencrypted over the network."
        )
        mcq(
            "What is a hash primarily used for?",
            ["Confidentiality", "Integrity checking", "Improving Wi‑Fi speed", "Replacing backups"],
            1,
            "Hashes let you detect changes (integrity). Encryption is primarily for confidentiality.",
            "crypto",
            "A hash produces a fixed-size digest used to verify data integrity — any change alters the hash."
        )
        mcq(
            "Which backup approach best supports fast recovery from accidental deletion for end users?",
            ["No backups; rely on antivirus", "Versioned backups / file history style versioning", "Only a yearly full backup", "Only a RAID array"],
            1,
            "Versioned backups allow restoring previous versions quickly; RAID isn’t a backup.",
            "backup",
            "Keep versioned backups or file history so users can restore prior versions quickly."
        )
        mcq(
            "What is an IDS designed to do?",
            ["Detect suspicious activity and alert", "Block all traffic automatically", "Encrypt network packets end-to-end", "Replace patching"],
            0,
            "An IDS detects and alerts; an IPS can also attempt blocking/prevention.",
            "ids,ips",
            "An Intrusion Detection System monitors for suspicious activity and raises alerts."
        )
        mcq(
            "Which is a reasonable way to improve password security in an organisation?",
            ["Allow short passwords for convenience", "Enforce minimum length + complexity + lockout policy", "Share one admin account for all staff", "Disable audit logging"],
            1,
            "Stronger password controls plus lockout reduce brute force and credential stuffing risk.",
            "access",
            "Enforce minimum strength, complexity, and lockout policies to reduce brute-force attacks."
        )

        cur.executemany("""
            INSERT INTO quiz_questions (unit_id, q_type, question, choices_json, answer_index, explanation, tags, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, qs)

    con.commit()
    con.close()
