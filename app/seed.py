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
        cur.executemany("INSERT INTO assessment_events (unit_id, name, kind) VALUES (?, ?, ?);", events)

        # Starter cards (keep your existing idea)
        cards = [
            (
                uid["ICTNWK421"],
                "Knowledge",
                "Define least privilege. Give 2 network examples.",
                "Least privilege means only the minimum access required. Examples: restrict admin access to management VLAN only; allow only required ports to servers; role-based accounts on devices.",
                "security,principles",
            ),
            (
                uid["ICTNWK421"],
                "Knowledge",
                "Stateful vs stateless firewall: what’s the difference?",
                "Stateful tracks connection state and allows return traffic automatically; stateless evaluates each packet independently against rules.",
                "firewall",
            ),
            (
                uid["ICTNWK421"],
                "Knowledge",
                "What does 'default deny' mean and why use it?",
                "Block by default, allow only explicitly required traffic; reduces attack surface and mistakes.",
                "policy",
            ),
            (
                uid["ICTNWK423"],
                "Knowledge",
                "Define data integrity and give 3 controls that support it.",
                "Integrity means data is accurate and not improperly changed. Controls: hashing/checksums, access control/least privilege, audit logging/change control, backups + restore testing.",
                "integrity,controls",
            ),
            (
                uid["ICTNWK423"],
                "Knowledge",
                "Hashing vs encryption: what does each provide?",
                "Hashing supports integrity verification (detect change). Encryption provides confidentiality (and with authentication can support integrity).",
                "crypto",
            ),
            (
                uid["ICTNWK423"],
                "Knowledge",
                "What is restore testing and why is it mandatory?",
                "Regularly restoring from backups to confirm backups are usable and meet RPO/RTO; otherwise backups might be corrupt or incomplete.",
                "backup",
            ),
        ]
        cur.executemany("INSERT INTO cards (unit_id, event_kind, prompt, answer, tags) VALUES (?, ?, ?, ?, ?);", cards)

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
            add(
                "AE2-T1.1",
                "Task 1.1 – Org structure + link to integrity/security",
                "Case Study",
                10,
                """
Write ~75 words.

- Organisation structure (teams/roles, reporting lines).
- Main business functions (what they do day-to-day).
- How structure/functions affect data integrity + security (controls, approvals, access, responsibilities).

Answer:
""",
                75,
            )

            add(
                "AE2-T1.2",
                "Task 1.2 – Recommend 2 current networking technologies",
                "Case Study",
                20,
                """
Write ~150 words (point form allowed).

For each technology:
- Features/capabilities (security-relevant).
- Example use at Millennium Media (where/why).
- How it supports security requirements.

Tech 1:
Tech 2:
""",
                150,
            )

            add(
                "AE2-T1.3-1",
                "Task 1.3 (1) – Privacy legislation + guideline",
                "Case Study",
                30,
                """
Fill the table (about ~60 words each row).

| Privacy Legislation/Guideline | Description | How it relates to MM security requirements |
|---|---|---|
|  |  |  |
|  |  |  |

""",
                120,
            )

            add(
                "AE2-T1.3-2",
                "Task 1.3 (2) – Two privacy issues",
                "Case Study",
                31,
                """
Fill the table (~75 words per issue).

| Privacy issue | Description | How it relates to integrity/security requirements |
|---|---|---|
|  |  |  |
|  |  |  |

""",
                150,
            )

            add(
                "AE2-T1.4",
                "Task 1.4 – Two reliable security info sources",
                "Case Study",
                40,
                """
Fill the table (~50 words per source). Include URL.

| Security source (name + URL) | What it provides | How it supports MM network security needs |
|---|---|---|
|  |  |  |
|  |  |  |

""",
                100,
            )

            add(
                "AE2-T1.5",
                "Task 1.5 – 4 environmental threats (Penrith) + risk analysis",
                "Case Study",
                50,
                """
Research local environmental threats relevant to data security and complete:

| Item | Threat | Potential damage | Likelihood (Low/Med/High + why) |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |

""",
                200,
            )

            add(
                "AE2-T1.6",
                "Task 1.6 – Two protection systems/controls for environmental threats",
                "Case Study",
                60,
                """
Pick two threats from Task 1.5 and complete:

| Item | Threat | System/Controls | Explanation (how it protects data) |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |

""",
                120,
            )

            add(
                "AE2-T1.7",
                "Task 1.7 – Two backup types + plan + backup/restore + rollback overview",
                "Case Study",
                70,
                """
Complete each part (point form ok, ~50 words each).

a) Two backup types (name + short description):
b) Recommendation plan (solution, type, schedule, location):
c) Procedure overview: backup + restore:
d) Procedure overview: rollback to earlier state:

Answer:
""",
                200,
            )

            add(
                "AE2-T1.8",
                "Task 1.8 – Identify threats/vulns by asset category + prioritise",
                "Case Study",
                80,
                """
Provide 2 threats/vulns for each category, explain why they could exist, then prioritise 1–4 with reasoning.

| Asset category | Threats & vulnerabilities (2 + short why) | Priority (1–4) + why |
|---|---|---|
| Network |  |  |
| Software |  |  |
| Hardware |  |  |
| User access |  |  |

""",
                200,
            )

            add(
                "AE2-T1.9",
                "Task 1.9 – Two network performance monitoring tools + compatibility",
                "Case Study",
                90,
                """
Include tool + URL (if applicable) and explain compatibility.

| Tool identification | Explanation of compatibility with MM network |
|---|---|
|  |  |
|  |  |

""",
                100,
            )

            # Part 2: Research questions (key ones you’ll answer in tables)
            add(
                "AE2-Q2.1",
                "Q2.1 – Tools: monitoring, hashing/encryption, backup/disaster recovery",
                "Research",
                110,
                """
Fill the table (~50–100 words each row).

| Function | Software product name + vendor | Overview of features/capabilities |
|---|---|---|
| Manage/monitor medium–large network |  |  |
| Hashing or encryption (integrity/confidentiality) |  |  |
| Backup/disaster recovery |  |  |

References (paste URLs):
- 
- 
""",
            )

            add(
                "AE2-Q2.2",
                "Q2.2 – Secure remote access: SSH vs Telnet + SSH encryption standards",
                "Research",
                120,
                """
a) SSH vs Telnet (purpose + comparison):
b) SSH encryption standards (overview: what’s used and why it’s secure):

Answer:

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.3",
                "Q2.3 – HTTPS, DNS, DHCP (purpose + functionality)",
                "Research",
                130,
                """
| Protocol | Description (20–40 words) |
|---|---|
| HTTPS |  |
| DNS |  |
| DHCP |  |

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.4",
                "Q2.4 – Eavesdropping, interception, corruption, falsification",
                "Research",
                140,
                """
| Threat | Description (~50 words) |
|---|---|
| Eavesdropping |  |
| Data interception |  |
| Data corruption |  |
| Data falsification |  |

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.5",
                "Q2.5 – Firewall roles/procedures across LAN/WLAN/WAN/DMZ/TCP/IP/app protocols",
                "Research",
                150,
                """
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
""",
            )

            add(
                "AE2-Q2.6",
                "Q2.6 – Security perimeter + enterprise perimeter hardware (incl firewall)",
                "Research",
                160,
                """
a) Define security perimeter + functions (about ~100 words):
b) Two enterprise perimeter hardware products + features/capabilities (include a hardware firewall):

Answer:

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.7",
                "Q2.7 – VPN concepts (encryption, firewall considerations, tunnelling, auth)",
                "Research",
                170,
                """
| VPN concept | Description |
|---|---|
| Data encryption |  |
| Firewall considerations |  |
| Packet tunnelling |  |
| Authentication process |  |

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.8",
                "Q2.8 – VPN types: site-to-site, client-to-site, extranet",
                "Research",
                180,
                """
| VPN type | Description |
|---|---|
| Site-to-site |  |
| Client-to-site (user-to-site) |  |
| Extranet |  |

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.9",
                "Q2.9 – Two antivirus solutions + scanning techniques (screenshots if relevant)",
                "Research",
                190,
                """
| Item | Solution | Techniques (how to scan + what to check) |
|---|---|---|
| 1 |  |  |
| 2 |  |  |

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.10",
                "Q2.10 – Tools/procedures: auditing, IDS, penetration testing",
                "Research",
                200,
                """
| Function | Product name | Procedure summary (how you’d use it) |
|---|---|---|
| Network access auditing |  |  |
| Intrusion detection |  |  |
| Penetration testing |  |  |

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.11",
                "Q2.11 – Three monitoring/security tools (features + 2 capabilities)",
                "Research",
                210,
                """
| Tool | General features | 2 functions/capabilities |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

References (paste URLs):
- 
""",
            )

            add(
                "AE2-Q2.12",
                "Q2.12 – Demonstrate backup + restore (systems/procedures)",
                "Research",
                220,
                """
| Item | Systems and procedures (~50 words each) |
|---|---|
| Backup |  |
| Restore |  |

References (paste URLs):
- 
""",
            )

            cur.executemany(
                """
                INSERT INTO ae2_items (unit_id, code, title, section, order_index, template_md, word_guidance)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
                items,
            )

    # Seed quiz questions — re-seed if count is below expected or seed version changed
    EXPECTED_PER_UNIT = 80  # target ~80 MCQs per unit
    QUIZ_SEED_VERSION = "4"  # v4: expanded question bank + advanced scenarios

    cur.execute("SELECT value FROM settings WHERE key = 'quiz_seed_version';")
    row = cur.fetchone()
    quiz_version_changed = (row is None) or (row["value"] != QUIZ_SEED_VERSION)

    for ucode in ("ICTNWK421", "ICTNWK423"):
        u = cur.execute("SELECT id FROM units WHERE code = ?;", (ucode,)).fetchone()
        if not u:
            continue
        unit_id = int(u["id"])

        cur.execute("SELECT COUNT(*) AS n FROM quiz_questions WHERE unit_id = ?;", (unit_id,))
        if cur.fetchone()["n"] >= EXPECTED_PER_UNIT and not quiz_version_changed:
            continue

        # Clear old questions so we can re-seed cleanly (attempts cascade-delete)
        cur.execute("DELETE FROM quiz_questions WHERE unit_id = ?;", (unit_id,))

        qs = []

        def mcq(question, choices, answer_index, explanation, tags="", context=""):
            qs.append(
                (
                    unit_id,
                    "mcq",
                    question.strip(),
                    json.dumps(choices),
                    int(answer_index),
                    explanation.strip(),
                    tags,
                    context.strip(),
                )
            )

        # A solid starter pack (we can expand to 100+ later)
        mcq(
            "What does the principle of least privilege mean?",
            [
                "Grant broad access initially and restrict permissions after incidents occur",
                "Give only the minimum access needed to do the job",
                "Ensure every user has the same level of access for consistency and fairness",
                "Assign permissions based on department seniority and job tenure",
            ],
            1,
            "Least privilege means users/services get only the permissions required for their tasks, reducing impact if an account is compromised.",
            "principles",
            "Limit accounts to only the permissions they need to perform their job.",
        )
        mcq(
            "Which is the best description of a firewall’s main job?",
            [
                "Scan incoming files for malware signatures and quarantine threats",
                "Filter network traffic according to rules/policy",
                "Authenticate users before granting access to network resources",
                "Monitor network performance and optimise bandwidth allocation",
            ],
            1,
            "Firewalls enforce traffic policy at boundaries (and sometimes internally) by allowing/denying traffic based on rules.",
            "firewall",
            "A device or software that filters network traffic according to allow/deny rules.",
        )
        mcq(
            "Why is SSH preferred over Telnet for remote administration?",
            [
                "SSH supports more concurrent sessions than Telnet",
                "SSH encrypts the session; Telnet is plaintext",
                "SSH operates on a lower port number which improves security",
                "SSH uses compression by default while Telnet does not",
            ],
            1,
            "SSH provides encrypted remote access; Telnet sends credentials and commands in plaintext.",
            "ssh,telnet",
            "SSH encrypts terminal sessions; Telnet sends data unencrypted over the network.",
        )
        mcq(
            "What is a hash primarily used for?",
            [
                "Confidentiality — preventing unauthorised reading of data",
                "Integrity checking — detecting whether data has been altered",
                "Authentication — verifying user identity during login",
                "Non-repudiation — proving who sent a message",
            ],
            1,
            "Hashes let you detect changes (integrity). Encryption is primarily for confidentiality.",
            "crypto",
            "A hash produces a fixed-size digest used to verify data integrity — any change alters the hash.",
        )
        mcq(
            "Which backup approach best supports fast recovery from accidental deletion for end users?",
            [
                "Daily full backups stored on an external drive",
                "Versioned backups / file history style versioning",
                "Incremental backups taken weekly to a network share",
                "RAID 1 mirroring across two drives in the same machine",
            ],
            1,
            "Versioned backups allow restoring previous versions quickly; RAID isn’t a backup.",
            "backup",
            "Keep versioned backups or file history so users can restore prior versions quickly.",
        )
        mcq(
            "What is an IDS designed to do?",
            [
                "Detect suspicious activity and alert administrators",
                "Block malicious traffic inline and prevent attacks in real-time",
                "Filter traffic based on access control lists and firewall rules",
                "Scan endpoints for malware and quarantine infected files",
            ],
            0,
            "An IDS detects and alerts; an IPS can also attempt blocking/prevention.",
            "ids,ips",
            "An Intrusion Detection System monitors for suspicious activity and raises alerts.",
        )
        mcq(
            "Which is a reasonable way to improve password security in an organisation?",
            [
                "Require password changes every 7 days with no reuse restrictions",
                "Enforce minimum length + complexity + lockout policy",
                "Use a single strong shared password for each department",
                "Set maximum password length to 8 characters to reduce forgotten passwords",
            ],
            1,
            "Stronger password controls plus lockout reduce brute force and credential stuffing risk.",
            "access",
            "Enforce minimum strength, complexity, and lockout policies to reduce brute-force attacks.",
        )

        # ── ICTNWK421-specific questions (network security) ───────
        if ucode == "ICTNWK421":
            mcq(
                "What advantage does a stateful firewall have over a stateless one?",
                [
                    "It inspects application-layer payloads for malware signatures",
                    "It tracks connection state and allows legitimate return traffic automatically",
                    "It operates faster because it skips packet header inspection",
                    "It uses deep packet inspection to decrypt and analyse encrypted traffic",
                ],
                1,
                "Stateful firewalls remember active connections so return traffic is allowed without extra rules; stateless firewalls evaluate every packet independently.",
                "firewall",
                "Stateful inspection tracks each connection's state (new, established, related) and permits valid return traffic.",
            )
            mcq(
                "What does a 'default deny' firewall policy mean?",
                [
                    "All traffic is allowed unless it matches a specific deny rule",
                    "All traffic is blocked unless explicitly allowed by a rule",
                    "All outbound traffic is blocked but inbound traffic is permitted",
                    "All traffic from external sources is denied but internal traffic flows freely",
                ],
                1,
                "Default deny blocks everything by default; you create allow rules only for required traffic, reducing attack surface.",
                "firewall,principles",
                "A default deny policy blocks all traffic that is not explicitly permitted by a rule.",
            )
            mcq(
                "At which OSI layer does a packet-filtering firewall primarily operate?",
                [
                    "Application (Layer 7) — inspecting HTTP and FTP commands",
                    "Network and Transport (Layers 3-4) — examining IP addresses and ports",
                    "Data Link (Layer 2) — filtering based on MAC addresses",
                    "Session (Layer 5) — managing connection dialogues between hosts",
                ],
                1,
                "Packet-filtering firewalls inspect IP addresses and port numbers at Layers 3-4.",
                "firewall",
                "Packet-filtering firewalls examine headers at the network (IP) and transport (TCP/UDP) layers.",
            )
            mcq(
                "What does an application-layer (proxy) firewall inspect that a packet filter cannot?",
                [
                    "Source and destination IP addresses in the packet header",
                    "The actual content and payload of application protocols like HTTP",
                    "TCP sequence numbers and window sizes for flow control",
                    "VLAN tags and 802.1Q headers on trunk ports",
                ],
                1,
                "Application-layer firewalls understand protocols like HTTP/FTP and can inspect payloads, URLs, and commands.",
                "firewall",
                "A proxy firewall operates at Layer 7 and can inspect application data inside packets.",
            )
            mcq(
                "What is the purpose of a site-to-site VPN?",
                [
                    "Allow individual remote workers to securely access corporate email",
                    "Securely link two entire networks over the internet",
                    "Encrypt traffic between a client device and a public Wi-Fi hotspot",
                    "Create an isolated guest network within a single office location",
                ],
                1,
                "Site-to-site VPNs create an encrypted tunnel between two networks (e.g. branch office to head office).",
                "vpn",
                "A site-to-site VPN connects two entire networks securely over an untrusted link like the internet.",
            )
            mcq(
                "When would you use a client-to-site (remote access) VPN?",
                [
                    "To permanently connect two branch office networks together",
                    "To let a remote worker securely access the corporate network",
                    "To create a secure link between two data centres for replication",
                    "To segment internal network traffic between different VLANs",
                ],
                1,
                "Client-to-site VPNs let individual users tunnel into the corporate network from any location.",
                "vpn",
                "A client-to-site VPN lets a single remote user create an encrypted tunnel to the organisation's network.",
            )
            mcq(
                "What does encryption in a VPN primarily protect against?",
                [
                    "Denial-of-service attacks flooding the VPN gateway",
                    "Eavesdropping on data in transit",
                    "Brute-force attacks against user passwords",
                    "Unauthorised physical access to network devices",
                ],
                1,
                "VPN encryption ensures that data intercepted in transit cannot be read by attackers.",
                "vpn,crypto",
                "VPN encryption scrambles traffic so it is unreadable to anyone intercepting it between endpoints.",
            )
            # ── ICTNWK421 advanced security questions ─────────
            mcq(
                "What does Port Address Translation (PAT) allow that standard NAT does not?",
                [
                    "Assign a single public IP to each private host",
                    "Map multiple private hosts to a single public IP using different source ports",
                    "Remove port information so traffic is anonymous",
                    "Translate application-layer payloads to conform with policy",
                ],
                1,
                "PAT maps many private hosts to one public IP by translating source ports, preserving the ability to share a single IP.",
                "nat,firewall",
                "PAT creates unique translations per source port so multiple internal hosts can share one public IP.",
            )
            mcq(
                "Why does a stateful firewall rate connections differently than a packet filter?",
                [
                    "It monitors throughput to throttle high bandwidth flows",
                    "It remembers the handshake state so returning packets are allowed without extra rules",
                    "It enforces per-user authentication on each packet",
                    "It operates at Layer 2 which is faster than packet filters",
                ],
                1,
                "Stateful firewalls store connection state so replies belonging to established sessions are permitted automatically.",
                "firewall,stateful",
                "Stateful inspection tracks flags like SYN/ACK so it can tie inbound packets to prior outbound sessions.",
            )
            mcq(
                "Which is the best role for an application-layer firewall compared with a network firewall?",
                [
                    "Block all ICMP and ARP traffic across VLANs",
                    "Inspect and filter HTTP/FTP requests by validating headers and payload",
                    "Replace IDS sensors because it prevents all intrusions",
                    "Perform NAT for internal hosts only",
                ],
                1,
                "Application firewalls examine protocol content (URL, headers) and can block attacks hidden in payloads.",
                "firewall,proxy",
                "Proxy firewalls operate at Layer 7 so they can inspect URLs, HTTP methods, and payloads.",
            )
            mcq(
                "Why is logging allowed and denied packets helpful on a firewall?",
                [
                    "It prevents attackers from seeing the firewall status page",
                    "It builds an audit trail to detect repeated attack patterns and tune rules",
                    "It encrypts logs so the firewall can be remote managed",
                    "It alerts the SIEM to automatically patch services",
                ],
                1,
                "Firewall logging reveals blocked attempts and unusual patterns so analysts can adjust rules or escalate incidents.",
                "logs,audit",
                "Log both allowed and denied traffic to identify misconfigured rules and malicious behaviour.",
            )
            mcq(
                "When configuring NAT traversal for VoIP, what must you do?",
                [
                    "Enable symmetric encryption on all RTP streams",
                    "Allow the same UDP port through the firewall and map it via PAT",
                    "Disable SIP ALG on the firewall and allow a range of UDP ports",
                    "Only allow RTP on TCP port 443",
                ],
                2,
                "VoIP needs a range of UDP ports open so RTP can traverse; SIP ALG often breaks the signalling, so disable it.",
                "nat,voip",
                "Allow the required UDP port range and disable SIP ALG so signalling stays intact.",
            )
            mcq(
                "What principle does Zero Trust architecture emphasise?",
                [
                    "Trust every internal request but verify external ones",
                    "Verify continuously and treat every request as potentially hostile",
                    "Use a single perimeter firewall to protect the entire network",
                    "Allow access based only on physical presence and device type",
                ],
                1,
                "Zero Trust assumes the network is hostile and requires continuous verification before granting access.",
                "zerotrust,architecture",
                "Zero Trust means 'never trust, always verify' — every request must be authenticated and authorised.",
            )
            mcq(
                "Which control best supports a micro-segmentation strategy?",
                [
                    "Splitting the network into hardware VLANs with a single ACL per VLAN",
                    "Using software-defined policies to restrict east-west traffic between workloads",
                    "Allowing all internal traffic by default because it is low risk",
                    "Routing all VLANs through one flat switch",
                ],
                1,
                "Micro-segmentation uses fine-grained policies to control traffic between workloads, limiting lateral movement.",
                "segmentation",
                "Software-defined micro-segmentation can enforce policies between workloads even within the same VLAN.",
            )
            mcq(
                "In the shared responsibility model for cloud security, what does the provider handle?",
                [
                    "User awareness training",
                    "Hypervisor, physical hosts, and the compute/storage infrastructure",
                    "Application-level authentication for customer apps",
                    "Data classification and backup strategy",
                ],
                1,
                "Cloud providers secure the physical infrastructure and hypervisor; customers secure applications and data.",
                "cloud,model",
                "Public cloud providers manage hardware, hypervisor, and foundational services; customers secure workloads on top.",
            )
            mcq(
                "Which practice best mitigates social engineering phishing attacks?",
                [
                    "Allow executives to bypass MFA because they are trusted",
                    "Disable email filters to let every message through for auditing",
                    "Train staff to verify sender addresses and avoid clicking links from unknown sources",
                    "Store passwords in spreadsheets so they can be shared quickly",
                ],
                2,
                "User training to spot phishing plus verification prevents malicious actors from harvesting credentials.",
                "socialengineering,training",
                "Educate staff to verify unexpected emails, never send credentials, and report suspicious requests.",
            )
            mcq(
                "During which penetration testing phase do you gather network topology and system inventory?",
                ["Reconnaissance", "Exploitation", "Reporting", "Post-exploitation"],
                0,
                "Reconnaissance collects OSINT and network data before attempting exploits.",
                "pentest,stages",
                "Reconnaissance identifies targets, services, and topology using non-intrusive methods.",
            )
            mcq(
                "Which action describes the exploitation phase of penetration testing?",
                [
                    "Documenting control weaknesses and mitigation suggestions",
                    "Observing network traffic to understand topology",
                    "Using a crafted payload to gain initial access",
                    "Scheduling the assessment and scoping rules",
                ],
                2,
                "Exploitation uses vulnerabilities to gain access, after reconnaissance and scanning stages.",
                "pentest",
                "The exploitation stage leverages vulnerabilities to breach a system and demonstrate risk.",
            )
            mcq(
                "How does a vulnerability scan differ from a penetration test?",
                [
                    "Scans simulate attacks while penetration tests simply run compliance scripts",
                    "Scans identify potential weaknesses automatically; penetration tests attempt to exploit those weaknesses",
                    "Penetration tests are automated while vulnerability scans always require human oversight",
                    "Scans repair issues immediately after detection",
                ],
                1,
                "Vulnerability scans flag issues; pen testers attempt to exploit them for real-world impact.",
                "scan,penetration",
                "Scanning identifies possible vulnerabilities; penetration testing attempts to exploit them.",
            )
            mcq(
                "What is one advantage of using WireGuard over traditional IPsec VPNs?",
                [
                    "WireGuard requires per-user certificates managed manually",
                    "WireGuard operates with fewer configuration options and a smaller codebase",
                    "WireGuard encrypts only metadata while IPsec encrypts the entire packet",
                    "WireGuard is only compatible with proprietary hardware",
                ],
                1,
                "WireGuard has a minimal codebase and simpler configuration, reducing attack surface and complexity.",
                "vpn,wireguard",
                "WireGuard is lightweight and easy to configure compared to legacy IPsec implementations.",
            )
            mcq(
                "How does TLS ensure server authenticity during a VPN handshake?",
                [
                    "The server sends its credential to the CA every 12 hours",
                    "The server presents a certificate signed by a trusted CA and the client verifies it",
                    "TLS skips authentication because the tunnel is already encrypted",
                    "The server uses SHA-1 to hash the password and sends it in plaintext",
                ],
                1,
                "TLS servers present certificates signed by a CA; clients verify the signature against trusted roots.",
                "tls,vpn",
                "Clients use the CA-signed server certificate to confirm the server’s identity before exchanging keys.",
            )
            mcq(
                "Which strategy improves security on IoT devices?",
                [
                    "Connect IoT devices into the main VLAN with no filtering",
                    "Segment IoT devices into a dedicated VLAN with strict ACLs and monitoring",
                    "Disable logging to preserve limited device storage",
                    "Allow remote management from the internet without firewall rules",
                ],
                1,
                "Segmenting IoT devices limits access and reduces the blast radius if a device is compromised.",
                "iot,segmentation",
                "Use VLANs/ACLs and monitoring for IoT to reduce lateral movement risk.",
            )
            mcq(
                "How does a VLAN help reduce attack surface inside the LAN?",
                [
                    "By encrypting traffic between VLAN members automatically",
                    "By logically grouping hosts and restricting traffic between VLANs via ACLs",
                    "By eliminating the need for firewalls since VLANs isolate traffic completely",
                    "By broadcasting ARP responses to every VLAN",
                ],
                1,
                "VLANs group hosts logically and enforce ACLs at the router to control cross-VLAN traffic.",
                "vlan",
                "Use routers/firewalls between VLANs to control which segments can see each other.",
            )
            mcq(
                "Why send logs from firewalls and endpoints to a SIEM?",
                [
                    "To replace the need for IDS sensors",
                    "To aggregate events, detect patterns, and correlate incidents",
                    "To reduce log retention requirements",
                    "To automatically patch systems without review",
                ],
                1,
                "SIEMs correlate logs across sources, enabling detection of complex threats earlier.",
                "siem,logs",
                "Centralising logs allows pattern detection and faster incident response.",
            )
            mcq(
                "What is a key reason to keep security logs archived for at least 90 days?",
                [
                    "Support compliance audits and incident investigations",
                    "Ensure the firewall rule cache remains persistent",
                    "Prevent attackers from reading the logs older than 90 days",
                    "Allow production services to reuse the storage space quickly",
                ],
                0,
                "Retention supports forensic analysis and regulatory compliance after incidents.",
                "retention",
                "Store significant logs long enough to investigate past incidents and satisfy auditors.",
            )
            mcq(
                "Why implement multi-factor authentication (MFA)?",
                [
                    "To eliminate the need for strong passwords altogether",
                    "To combine two or more factors (knowledge, possession, inherence) for stronger assurance",
                    "To rely solely on geolocation checks for authentication",
                    "To allow password reuse across services",
                ],
                1,
                "MFA requires at least two different factor types, making unauthorized access harder even if a password is stolen.",
                "mfa,authentication",
                "Combine something you know (password) with something you have (token) or are (biometrics).",
            )
            mcq(
                "Which step is most important when hardening a Windows server before deployment?",
                [
                    "Installing as many features as possible for flexibility",
                    "Disabling unused services and ports to reduce the attack surface",
                    "Escalating all users to local administrator rights to avoid permission issues",
                    "Leaving default passwords because changing them may break scripts",
                ],
                1,
                "Turning off unused services and blocking unnecessary ports reduces exposure.",
                "hardening",
                "Disable services/ports you don’t need and apply secure configuration baselines.",
            )
            mcq(
                "What indicates a secure patch management process?",
                [
                    "Applying patches only when users report issues",
                    "Verifying vendor-supplied digital signatures before installing updates",
                    "Installing every available update immediately without testing",
                    "Maintaining a single monolithic update bundle for all systems",
                ],
                1,
                "Checking digital signatures ensures updates are authentic and untampered.",
                "patch,update",
                "Validate patch signatures and test them prior to wide deployment.",
            )
            mcq(
                "Why might an organisation deploy honeypots inside the network?",
                [
                    "To serve as primary business servers for high availability",
                    "To distract attackers and collect forensic data on their methods",
                    "To replace firewalls and simplify network architecture",
                    "To host legally protected customer data",
                ],
                1,
                "Honeypots lure attackers and capture tactics without risking production assets.",
                "honeypot",
                "Use honeypots to observe attacker behaviour and improve detection.",
            )
            mcq(
                "Which technique helps mitigate volumetric DDoS attacks?",
                [
                    "Using a dedicated SIEM appliance on-premises",
                    "Sending all traffic through a single small office router",
                    "Deploying scrubbing services or anycast front-ends to absorb high-volume traffic",
                    "Allowing unlimited concurrent connections on the firewall",
                ],
                2,
                "Cloud-based scrubbing/anycast distributes traffic and removes malicious packets.",
                "ddos",
                "Use scrubbing centres or anycast distribution to handle large-scale DDoS traffic.",
            )
            mcq(
                "What is one reason to deploy a Web Application Firewall (WAF) in front of an HTTP service?",
                [
                    "To block all outbound traffic",
                    "To inspect HTTP payloads and block SQL injection/XSS before they reach the app",
                    "To accelerate database queries",
                    "To reduce the number of TLS certificates required",
                ],
                1,
                "WAFs filter HTTP requests for application-layer attacks such as injection and cross-site scripting.",
                "waf",
                "WAFs examine request bodies and headers, blocking malicious payloads.",
            )
            mcq(
                "How does DNS sinkholing enhance security?",
                [
                    "It allows DNS responses only for internal resources",
                    "It intercepts malicious DNS requests and redirects them to a safe server for logging",
                    "It increases DNS response time dramatically",
                    "It bypasses firewall rules for DNS traffic",
                ],
                1,
                "Sinkholes catch malicious domains and redirect traffic to safe hosts for analysis.",
                "dns",
                "Redirect suspicious DNS lookups to a controlled server to block malware callbacks.",
            )
            mcq(
                "Why would an organisation keep certain systems air-gapped?",
                [
                    "To allow them to connect to the internet without oversight",
                    "To completely isolate critical systems (e.g., SCADA, backups) preventing network-based compromise",
                    "To make updates easier by connecting them to all networks",
                    "To reduce cooling requirements",
                ],
                1,
                "Air-gapping isolates critical systems to prevent remote attackers from reaching them.",
                "airgap",
                "Air-gapped systems have no network connectivity, reducing their exposure.",
            )
            mcq(
                "Which authentication method pairs well with 802.1X for wireless access?",
                [
                    "Single-factor pre-shared key",
                    "RADIUS with device or user certificates",
                    "Open authentication with no password",
                    "MAC filtering alone",
                ],
                1,
                "802.1X uses RADIUS for user/device authentication, often with certificates or tokens.",
                "802.1X,wifi",
                "802.1X works with RADIUS and certificates/tokens to authenticate wireless clients.",
            )
            mcq(
                "How can you detect rogue access points?",
                [
                    "Trust any SSID that matches corporate naming",
                    "Use wireless monitoring tools to compare physical APs detected against inventory and location",
                    "Rely solely on security policy for BYOD",
                    "Allow all open networks so devices connect freely",
                ],
                1,
                "Monitoring tools identify unauthorized APs by comparing observed hardware with known inventory.",
                "rogue,monitoring",
                "Use RF scanning or IDS/IPS to find APs you didn’t deploy.",
            )
            mcq(
                "Which configuration change helps eliminate default credentials on network gear?",
                [
                    "Set the same password on all routers for easy recovery",
                    "Immediately change default usernames/passwords during commissioning",
                    "Allow vendor defaults to remain for vendor support purposes",
                    "Store default credentials in a shared spreadsheet offensive to interceptors",
                ],
                1,
                "Changing defaults reduces the risk of attackers using widely-known credentials.",
                "passwords,hardening",
                "Update default credentials before connecting devices to the network.",
            )
            mcq(
                "What best practice supports BYOD while maintaining security?",
                [
                    "Allow any personal device with no restrictions",
                    "Enforce a mobile device management profile with enforced policies and containerisation",
                    "Disable encryption on BYOD devices to simplify troubleshooting",
                    "Share admin credentials across personal devices",
                ],
                1,
                "MDM/EMM profiles enforce policies and can isolate corporate data on BYOD devices.",
                "byod,policy",
                "Require device management, encryption, and separation of corporate data on personal devices.",
            )
            mcq(
                "Which service helps maintain visibility of cloud posture?",
                [
                    "A legacy on-premises SIEM appliance",
                    "Cloud Security Posture Management (CSPM) to monitor misconfigurations continuously",
                    "Manual spreadsheet reviews done quarterly",
                    "Turning off cloud logging to reduce costs",
                ],
                1,
                "CSPM tools continuously check cloud accounts for misconfigurations and compliance violations.",
                "cspm,cloud",
                "Use CSPM scanning to ensure cloud resources stay within policy.",
            )
            mcq(
                "What is VPN tunnelling?",
                [
                    "Encrypting data at the application layer before it reaches the network stack",
                    "Encapsulating private network packets inside public network packets",
                    "Routing traffic through multiple proxy servers to hide the source IP",
                    "Compressing packets to reduce bandwidth usage across the WAN link",
                ],
                1,
                "Tunnelling wraps (encapsulates) private packets inside encrypted public packets for secure transport.",
                "vpn",
                "Tunnelling encapsulates one protocol's packets inside another to carry them securely across an untrusted network.",
            )
            mcq(
                "What is a benefit of SSH key-based authentication over password-only login?",
                [
                    "Keys allow multiple users to share the same login credentials securely",
                    "Keys are much harder to brute-force and the private key never travels over the network",
                    "Keys eliminate the need for encryption during the SSH session",
                    "Keys automatically expire after 90 days, enforcing regular rotation",
                ],
                1,
                "SSH keys use asymmetric cryptography; the private key never leaves the client, making brute-force impractical.",
                "ssh,access",
                "SSH key-based auth uses a public/private key pair; the private key stays on the client and is very difficult to brute-force.",
            )
            mcq(
                "What is the key difference between an IPS and an IDS?",
                [
                    "An IDS sits inline and blocks traffic; an IPS monitors passively from a span port",
                    "An IPS can block and prevent attacks inline; an IDS only detects and alerts",
                    "An IDS uses signature-based detection while an IPS uses anomaly-based only",
                    "An IPS operates at Layer 3 while an IDS operates at Layer 7 exclusively",
                ],
                1,
                "IDS = detect and alert. IPS = detect, alert, and can take action to block the threat.",
                "ids,ips",
                "An IPS sits inline and can actively block malicious traffic; an IDS passively monitors and alerts.",
            )
            mcq(
                "Where is a network-based IDS (NIDS) typically placed?",
                [
                    "Inline between the firewall and the internet, filtering all traffic",
                    "At a network tap or span port to monitor traffic passively",
                    "On each server as a software agent monitoring local processes",
                    "At the core switch replacing the default gateway for traffic analysis",
                ],
                1,
                "A NIDS is placed where it can see network traffic, usually via a span/mirror port on a switch or a network tap.",
                "ids",
                "A network-based IDS monitors traffic by connecting to a span port or tap on a key network segment.",
            )
            mcq(
                "What is the purpose of a DMZ in network architecture?",
                [
                    "To provide a high-speed internal backbone connecting all VLANs",
                    "To host public-facing services in an isolated zone between internal and external networks",
                    "To create an encrypted tunnel for all external-facing traffic",
                    "To segment the wireless network from the wired network within the LAN",
                ],
                1,
                "A DMZ provides a buffer zone for public servers (web, email) so that a compromise does not directly expose the internal LAN.",
                "firewall,principles",
                "A DMZ (demilitarised zone) isolates public-facing servers from the internal network using firewalls.",
            )
            mcq(
                "What does HTTPS provide that HTTP does not?",
                [
                    "Server-side caching that improves page load times",
                    "Encryption of data between browser and server via TLS",
                    "Compression of web content to reduce bandwidth usage",
                    "Authentication of the client's identity to the web server",
                ],
                1,
                "HTTPS uses TLS to encrypt the connection, protecting data confidentiality and integrity in transit.",
                "crypto",
                "HTTPS layers TLS encryption over HTTP, protecting data exchanged between client and server.",
            )
            mcq(
                "What is DNS cache poisoning?",
                [
                    "Overloading a DNS server with requests to cause a denial of service",
                    "Inserting false DNS records so users are redirected to malicious sites",
                    "Intercepting DNS queries to monitor which websites users visit",
                    "Corrupting the DNS zone file by exploiting a buffer overflow on the server",
                ],
                1,
                "DNS poisoning tricks a resolver into caching a wrong IP for a domain, redirecting users to attacker-controlled servers.",
                "dns,threats",
                "DNS cache poisoning injects fraudulent records into a resolver's cache, redirecting traffic to malicious IPs.",
            )
            mcq(
                "What risk does a rogue DHCP server pose on a network?",
                [
                    "It exhausts the IP address pool, preventing legitimate devices from connecting",
                    "It can hand out incorrect gateway/DNS settings, enabling man-in-the-middle attacks",
                    "It assigns static IP addresses that conflict with existing reservations",
                    "It broadcasts SSIDs that mimic the legitimate wireless network",
                ],
                1,
                "A rogue DHCP server gives clients attacker-controlled settings (gateway, DNS), enabling traffic interception.",
                "dhcp,threats",
                "A rogue DHCP server distributes false network settings, potentially redirecting all client traffic through an attacker.",
            )
            mcq(
                "How does signature-based antivirus detection work?",
                [
                    "It analyses program behaviour at runtime to detect suspicious activity",
                    "It compares files against a database of known malware signatures and patterns",
                    "It uses machine learning to predict whether a file is likely malicious",
                    "It sandboxes every executable in a virtual environment before allowing it to run",
                ],
                1,
                "Signature-based AV matches file contents against known malware patterns; it needs regular signature updates.",
                "antivirus",
                "Signature-based detection compares files to a database of known malware patterns (signatures).",
            )
            mcq(
                "What is the main goal of a penetration test?",
                [
                    "To scan for known CVEs and produce an automated vulnerability report",
                    "To simulate real attacks and find exploitable vulnerabilities before attackers do",
                    "To verify that firewall rules match the organisation's security policy document",
                    "To test backup and restore procedures under disaster recovery conditions",
                ],
                1,
                "Pen tests simulate attacker techniques to discover weaknesses in systems, networks, and processes.",
                "audit,testing",
                "Penetration testing simulates real-world attacks to identify exploitable vulnerabilities in a controlled manner.",
            )
            mcq(
                "What does a network access audit primarily check?",
                [
                    "Whether network bandwidth meets the agreed service level targets",
                    "Who accessed what resources and whether access was authorised",
                    "Whether all devices on the network have current antivirus signatures",
                    "Whether firewall rules are optimised for maximum throughput",
                ],
                1,
                "Network audits review logs and access records to verify compliance, detect anomalies, and ensure proper authorisation.",
                "audit",
                "A network access audit reviews logs to verify that resource access was authorised and compliant with policy.",
            )
            mcq(
                "What type of attack is eavesdropping on a network?",
                [
                    "An active attack that injects malicious packets into the data stream",
                    "A passive attack that captures data without altering it",
                    "An active attack that modifies data in transit between hosts",
                    "A denial-of-service attack that disrupts network availability",
                ],
                1,
                "Eavesdropping is passive; the attacker listens to traffic without modifying it (e.g. packet sniffing).",
                "threats",
                "Eavesdropping is a passive attack where an attacker captures network traffic without altering it.",
            )
            mcq(
                "What is a man-in-the-middle (MITM) attack?",
                [
                    "An attacker floods a server with traffic to deny service to legitimate users",
                    "An attacker intercepts and potentially alters communication between two parties",
                    "An attacker exploits a software vulnerability to gain root access to a server",
                    "An attacker uses social engineering to trick a user into revealing credentials",
                ],
                1,
                "In a MITM attack, the attacker secretly relays/alters messages between two parties who believe they are communicating directly.",
                "threats",
                "A MITM attack intercepts communication between two parties, allowing the attacker to read or alter the data.",
            )
            mcq(
                "What does multi-factor authentication (MFA) require?",
                [
                    "Two or more credentials from the same factor type, such as a password and a PIN",
                    "Authentication from two or more different factor types (e.g. password + phone code)",
                    "A single strong authentication method such as a long passphrase or biometric scan",
                    "A password that is verified against two separate authentication servers for redundancy",
                ],
                1,
                "MFA combines factors from different categories: something you know, something you have, something you are.",
                "access,mfa",
                "MFA uses two or more distinct factor types: knowledge (password), possession (token/phone), or biometric.",
            )
            mcq(
                "What does 'defence in depth' mean?",
                [
                    "Deploying the strongest possible single security control at the network perimeter",
                    "Layering multiple security controls so that if one fails, others still protect",
                    "Focusing all security investment on the most likely threat vector identified in risk assessment",
                    "Hardening every system to the highest security standard before deployment",
                ],
                1,
                "Defence in depth uses multiple overlapping layers (firewall, IDS, AV, access control, etc.) so no single failure is catastrophic.",
                "principles",
                "Defence in depth layers multiple independent security controls so a single failure does not compromise the system.",
            )
            mcq(
                "Which protocol is commonly used for network device monitoring and management?",
                [
                    "Syslog — centralised log collection from network devices",
                    "SNMP — Simple Network Management Protocol for querying device status",
                    "NetFlow — captures and analyses traffic flow data between hosts",
                    "ICMP — used for ping and traceroute network diagnostics",
                ],
                1,
                "SNMP lets administrators query and monitor network devices (routers, switches, servers) for status, performance, and alerts.",
                "monitoring",
                "SNMP is used to monitor and manage network devices by querying status, performance counters, and alerts.",
            )
            mcq(
                "What is an Access Control List (ACL) on a router or firewall?",
                [
                    "A log of all successful and failed login attempts to the device",
                    "A set of rules that permit or deny traffic based on IP, port, or protocol",
                    "A directory of user accounts and their assigned VLAN memberships",
                    "A database of MAC addresses authorised to connect to switch ports",
                ],
                1,
                "ACLs are ordered rules on network devices that filter traffic by matching source/destination addresses, ports, and protocols.",
                "firewall,access",
                "An ACL is an ordered set of permit/deny rules applied to traffic based on IP addresses, ports, and protocols.",
            )
            mcq(
                "What is data falsification in a network security context?",
                [
                    "Intercepting data in transit to read confidential information",
                    "Deliberately altering data to deceive or cause harm",
                    "Accidentally corrupting data due to a hardware failure or software bug",
                    "Destroying data to prevent it from being recovered during an investigation",
                ],
                1,
                "Data falsification is the intentional, unauthorised modification of data to mislead or cause damage.",
                "threats",
                "Data falsification means deliberately modifying data without authorisation, compromising its integrity and trustworthiness.",
            )

            # Wireless security (WPA2/WPA3, 802.1X, rogue APs)
            mcq(
                "Why is WPA2/WPA3 preferred over WEP for securing a wireless network?",
                [
                    "WPA2/WPA3 use stronger encryption and key management than WEP, which is easily cracked",
                    "WEP supports longer SSIDs and more channels than WPA2/WPA3",
                    "WPA2/WPA3 operate only on the 5 GHz band, avoiding interference",
                    "WEP is designed specifically for enterprise networks with RADIUS servers",
                ],
                0,
                "WEP is considered broken; WPA2/WPA3 provide strong encryption (CCMP/AES) and better key management, making attacks far harder.",
                "wireless,crypto",
                "Think about how easy it is to crack a WEP key compared to WPA2/WPA3.",
            )
            mcq(
                "What is the main purpose of 802.1X in a wireless network?",
                [
                    "To automatically assign SSIDs based on device type",
                    "To provide port-based network access control using EAP authentication",
                    "To increase Wi‑Fi throughput by optimising channel bonding",
                    "To enable mesh networking between access points",
                ],
                1,
                "802.1X provides port-based access control; clients must authenticate (often via RADIUS) before gaining full network access.",
                "wireless,access",
                "802.1X is often used with WPA2/WPA3-Enterprise for authenticated Wi‑Fi.",
            )
            mcq(
                "What is a rogue access point?",
                [
                    "An access point configured for guest access with a captive portal",
                    "An unauthorised access point connected to the network, potentially bypassing security controls",
                    "An access point that uses a hidden SSID to avoid detection",
                    "An access point operating on a non-standard Wi‑Fi channel",
                ],
                1,
                "A rogue AP is an unauthorised device that extends the network, often without proper security, creating a serious vulnerability.",
                "wireless,threats",
                "Rogue APs may be plugged into wall ports or created by users with personal hotspots.",
            )
            mcq(
                "Which configuration best secures a corporate Wi‑Fi network for staff devices?",
                [
                    "Open SSID with MAC filtering only",
                    "WPA2/WPA3-Enterprise with 802.1X and unique credentials per user",
                    "WEP with a long shared key rotated yearly",
                    "Pre-shared WPA2 key shared among all staff and contractors",
                ],
                1,
                "Enterprise mode with 802.1X gives per-user credentials and centralised auth/logging; shared keys are weaker and hard to rotate.",
                "wireless,access",
                "Per-user authentication and logging are critical for accountability on Wi‑Fi.",
            )
            mcq(
                "What security risk is introduced by using an open Wi‑Fi network (no encryption)?",
                [
                    "Devices will not be able to obtain IP addresses from DHCP servers",
                    "Any traffic not using its own encryption can be intercepted and read by anyone nearby",
                    "The wireless signal cannot travel as far as with encryption enabled",
                    "Access points will automatically reduce their transmit power",
                ],
                1,
                "Open networks provide no link-layer encryption, allowing eavesdropping and session hijacking for unencrypted traffic.",
                "wireless,threats",
                "Think of coffee shop Wi‑Fi and what others on the network could see.",
            )

            # VLANs and segmentation
            mcq(
                "What is the primary security benefit of using VLANs in a switched network?",
                [
                    "They encrypt all traffic between switches by default",
                    "They logically separate broadcast domains, limiting which devices can directly communicate",
                    "They automatically block all inter-VLAN traffic",
                    "They provide automatic redundancy if a switch fails",
                ],
                1,
                "VLANs segment networks into smaller broadcast domains; combined with routing and ACLs they limit lateral movement.",
                "vlan,segmentation",
                "Segmentation limits the spread of attacks and confines sensitive systems.",
            )
            mcq(
                "How can VLANs help protect sensitive servers from compromise?",
                [
                    "By placing all devices, including servers and clients, into a single large VLAN",
                    "By placing servers in a dedicated VLAN with firewall/ACL rules controlling which VLANs can talk to them",
                    "By enabling spanning tree protocol on all switches",
                    "By disabling DHCP on the server VLAN",
                ],
                1,
                "Placing servers in dedicated VLANs and filtering traffic between VLANs restricts which devices can reach them.",
                "vlan,firewall",
                "Use VLANs plus ACLs/firewalls to implement network zones (e.g. servers, users, management).",
            )
            mcq(
                "What is a potential weakness if inter-VLAN routing is done on a core switch with no ACLs?",
                [
                    "Broadcast storms cannot be controlled between VLANs",
                    "All VLANs can communicate freely, reducing the benefit of segmentation",
                    "Spanning tree will disable inter-VLAN links",
                    "DHCP will not function correctly across VLANs",
                ],
                1,
                "Without ACLs or firewall rules, inter-VLAN routing effectively flattens the network, allowing lateral movement.",
                "vlan,threats",
                "Segmentation must be enforced with policy, not just VLAN tags.",
            )

            # PKI / certificate management
            mcq(
                "What is the primary purpose of a digital certificate in TLS?",
                [
                    "To encrypt user passwords before they are stored in a database",
                    "To bind a public key to an identity, allowing clients to verify they are talking to the correct server",
                    "To compress web content before transmission",
                    "To provide multi-factor authentication for VPN clients",
                ],
                1,
                "Certificates bind keys to identities (e.g. DNS names); clients verify the certificate chain to avoid MITM.",
                "pki,crypto",
                "Think of the padlock icon in a browser and how it knows which server it is talking to.",
            )
            mcq(
                "Why is it dangerous to ignore certificate warnings in a browser?",
                [
                    "It may reduce page load performance and caching efficiency",
                    "It could indicate a man-in-the-middle attack or misconfigured server, so continuing might expose credentials or data",
                    "It will permanently block access to that website",
                    "It means the website is using outdated HTML and CSS standards",
                ],
                1,
                "Certificate errors can indicate MITM or mis-issuance; ignoring them can expose confidential data.",
                "pki,threats",
                "Treat certificate warnings as serious until investigated.",
            )
            mcq(
                "What is certificate revocation used for?",
                [
                    "To reset a user's password after they forget it",
                    "To mark a certificate as no longer trusted before its normal expiry date",
                    "To extend the validity period of an expiring certificate",
                    "To rotate symmetric encryption keys used by TLS",
                ],
                1,
                "Revocation lets issuers invalidate certificates (e.g. after key compromise) so clients stop trusting them.",
                "pki",
                "CRLs and OCSP are common revocation mechanisms.",
            )

            # Incident response
            mcq(
                "What is the FIRST step in a formal incident response process after detecting a potential security incident?",
                [
                    "Eradication – remove all malicious software from affected systems",
                    "Containment – immediately disconnect all systems from the network",
                    "Identification – confirm and classify the incident based on evidence",
                    "Recovery – restore from backups to a known-good state",
                ],
                2,
                "You must first identify and confirm the incident, understand scope and type, before planning containment and eradication.",
                "incident",
                "Many frameworks describe phases: preparation, identification, containment, eradication, recovery, lessons learned.",
            )
            mcq(
                "During incident containment, which action is generally MOST appropriate?",
                [
                    "Immediately wipe and rebuild all servers involved",
                    "Isolate affected systems from the network while preserving evidence",
                    "Silently ignore the incident to avoid alarming users",
                    "Publicly disclose all details of the incident on social media",
                ],
                1,
                "Containment focuses on limiting damage while preserving logs and forensic evidence for analysis.",
                "incident,threats",
                "Avoid destroying evidence or causing unnecessary panic.",
            )
            mcq(
                "Why is it important to perform a post-incident review (lessons learned)?",
                [
                    "To identify which staff should be blamed for the incident",
                    "To improve controls, procedures, and training so similar incidents are less likely or less severe in future",
                    "To reduce the need for audit logging",
                    "To justify reducing the security budget if the incident was small",
                ],
                1,
                "Lessons learned help strengthen controls and processes, closing gaps revealed by the incident.",
                "incident,risk",
                "Incident reviews should be constructive, not punitive.",
            )

        # ── ICTNWK423-specific questions (data/network integrity) ─
        if ucode == "ICTNWK423":
            # ── ICTNWK423 additional data integrity questions ──────
            mcq(
                "What is an immutable backup?",
                [
                    "A backup kept on the same storage as the production system",
                    "A backup that cannot be altered or deleted once written",
                    "A backup that automatically compresses duplicate files",
                    "A backup that is stored only on tape and never restored",
                ],
                1,
                "Immutable backups are write-once so attackers cannot modify or delete them, supporting ransomware recovery.",
                "backup,ransomware",
                "Write-once storage prevents attackers from altering or deleting backup files.",
            )
            mcq(
                "Why store a copy of backups air-gapped offline?",
                [
                    "To allow external auditors to inspect the backup media easily",
                    "To keep a copy disconnected from networks so ransomware cannot reach it",
                    "To reduce restore times by keeping data on local disk",
                    "To avoid encrypting the backup data",
                ],
                1,
                "Air-gapped copies are kept offline to survive ransomware or corruption affecting the primary network.",
                "backup,ransomware",
                "Storing backups offline (air-gapped) isolates them from network-based attacks.",
            )
            mcq(
                "Which practice protects SaaS data like Office 365 from accidental deletion?",
                [
                    "Rely solely on provider retention policies",
                    "Implement a third-party SaaS backup that copies data to your own storage",
                    "Use MFA for SaaS logins and nothing else",
                    "Store data only locally and stop using SaaS",
                ],
                1,
                "Providers may not retain deleted objects indefinitely; independent backups let you restore user data regardless.",
                "backup,cloud",
                "Use third-party SaaS backup tools to capture and retain Salesforce/Office365 data that the provider might purge.",
            )
            mcq(
                "In the cloud shared responsibility model for IaaS, what does the customer control?",
                [
                    "Physical racks and hypervisor patches",
                    "The guest OS, applications, data, and identity management",
                    "Cooling, power distribution, and physical security",
                    "Underground cabling routes between datacentres",
                ],
                1,
                "IaaS customers manage their OS, apps, data, and user access; the provider secures the underlying infrastructure.",
                "cloud,model",
                "IaaS customers secure the guest OS/app and data, while the provider secures hardware and virtualization.",
            )
            mcq(
                "What is the first step in ISO 31000 risk management?",
                ["Risk treatment", "Risk identification", "Risk monitoring", "Risk documentation"],
                1,
                "ISO 31000 begins with identifying risks before analysing, evaluating, and treating them.",
                "risk,iso31000",
                "First identify threats/vulnerabilities, then analyse, evaluate, treat, and monitor them.",
            )
            mcq(
                "What information does a risk register typically include?",
                [
                    "Only pricing for backup storage",
                    "Risk description, likelihood, impact, and mitigation owner",
                    "Daily user login counts",
                    "Physical GPS coordinates of all devices",
                ],
                1,
                "A risk register documents each risk along with likelihood, impact, owner, and controls.",
                "risk",
                "Record risk details, probability, impact, owner, and mitigation actions.",
            )
            mcq(
                "During the asset lifecycle, what happens in the disposal phase?",
                [
                    "Assigning a warranty to a new device",
                    "Securely wiping or destroying data before retiring hardware",
                    "Deploying the device into production VLANs",
                    "Documenting physical locations for new assets",
                ],
                1,
                "Disposal includes sanitising, wiping, or destroying data and securely decommissioning devices.",
                "asset,lifecycle",
                "Proper disposal removes sensitive data and devices from service securely.",
            )
            mcq(
                "What is a key forensic best practice when collecting evidence?",
                [
                    "Work directly on the original drive to save time",
                    "Create an exact bit-for-bit copy and work on the copy",
                    "Only capture artefacts from volatile memory",
                    "Share evidence copies with anyone interested",
                ],
                1,
                "Forensics requires cloning drives to preserve original evidence for court or investigation.",
                "forensics",
                "Clone the original media (bit-for-bit) and analyse the copy to keep the original untampered.",
            )
            mcq(
                "What does Business Impact Analysis (BIA) determine?",
                [
                    "Which firewall rules should be updated next quarter",
                    "The criticality of processes and the impact of downtime on operations",
                    "Password policy complexity requirements",
                    "The number of backup copies needed for compliance",
                ],
                1,
                "BIA assesses the impact of disruptions and helps prioritise recovery order for services.",
                "bia,disaster",
                "BIA categorises services by their criticality and acceptable downtime.",
            )
            mcq(
                "Why is data sovereignty important for Australian organisations?",
                [
                    "It mandates SaaS vendors skip encryption for local data",
                    "It ensures personal information stays within legal jurisdictions and complies with APPs",
                    "It allows vendors to store data anywhere without restriction",
                    "It replaces the need for risk assessments",
                ],
                1,
                "Data sovereignty requires respecting laws where data is stored; APPs may demand data remain in Australia.",
                "privacy,data",
                "Comply with laws that dictate where personal data may be stored and who can access it.",
            )
            mcq(
                "Under the Australian Privacy Act, how soon must organisations notify a breach that could cause serious harm?",
                [
                    "Within 30 days",
                    "Immediately, once feasible",
                    "When the annual report is published",
                    "Only when the customer asks",
                ],
                1,
                "Organisations must promptly notify affected individuals and OAIC when there is a likely serious breach.",
                "privacy,notification",
                "Notify impacted individuals and the OAIC as soon as practicable after identifying a serious breach.",
            )
            mcq(
                "Which scenario best demonstrates encryption at rest?",
                [
                    "TLS encrypts data during HTTPS sessions",
                    "EFS encrypts files stored on a disk so stolen drives remain unreadable",
                    "VPN encrypts traffic between remote workers",
                    "Email encryption using S/MIME",
                ],
                1,
                "Encryption at rest protects stored files (e.g. BitLocker/EFS) even if the drive is stolen.",
                "crypto",
                "Use disk/file encryption so data remains protected while it sits on storage.",
            )
            mcq(
                "How does DLP prevent sensitive data from leaving a network?",
                [
                    "It blocks all outbound traffic regardless of content",
                    "It inspects content and blocks or logs attempts to send sensitive keywords or files",
                    "It encrypts all outbound emails by default",
                    "It disables USB ports on all computers",
                ],
                1,
                "DLP solutions monitor output channels and enforce policies when defined keywords or patterns are detected.",
                "dlp,data",
                "DLP inspects email, web, and USB channels for sensitive data and blocks or alerts.",
            )
            mcq(
                "What is a practical benefit of immutable backups in ransomware response?",
                [
                    "Enable the backup admin to log into the backup console with shared keys",
                    "Ensure ransomware cannot encrypt or delete backups once written",
                    "Compress backups aggressively to save storage",
                    "Store backups on the same volume as production data",
                ],
                1,
                "Immutable backups cannot be altered, so ransomware cannot corrupt them even if it spreads widely.",
                "backup,ransomware",
                "Immutable storage means the backup file cannot be changed or deleted once written.",
            )
            mcq(
                "Why choose RAID 6 over RAID 5 in a large array?",
                [
                    "RAID 6 writes data twice for faster writes",
                    "RAID 6 uses dual parity, surviving two simultaneous disk failures",
                    "RAID 6 uses striping with mirroring for better throughput",
                    "RAID 6 requires fewer disks than RAID 5",
                ],
                1,
                "RAID 6's dual parity allows two disks to fail without data loss, making it suitable for large arrays.",
                "raid",
                "RAID 6 tolerates two disk failures because it stores two parity blocks per stripe.",
            )
            mcq(
                "What benefit does RAID 10 provide over RAID 5?",
                [
                    "Uses less disk space than RAID 5",
                    "Combines mirroring and striping for better performance and fault tolerance at the cost of capacity",
                    "Relies only on parity so it can rebuild faster",
                    "Does not require any controller to manage",
                ],
                1,
                "RAID 10 offers high performance and fault tolerance by mirroring striped sets, though it halves capacity.",
                "raid",
                "RAID 10 stripes mirrored pairs, giving excellent performance and redundancy at the cost of disk utilisation.",
            )
            mcq(
                "What is the purpose of a data retention policy?",
                [
                    "To keep data forever in case it is needed",
                    "To define how long information is stored before it's securely destroyed",
                    "To make backups more frequent",
                    "To automatically encrypt data after 90 days",
                ],
                1,
                "Retention policies balance legal/regulatory requirements with storage costs and privacy concerns.",
                "retention",
                "Specify retention periods to comply with laws and limit exposure from stale data.",
            )
            mcq(
                "Which backup type is best for SaaS apps with built-in redundancy?",
                [
                    "Full backup every minute",
                    "API-based exports that capture SaaS objects/data to customer storage",
                    "Rely on provider replication alone",
                    "Store everything in a spreadsheet on a shared drive",
                ],
                1,
                "API-based SaaS backups capture configuration and data, giving control beyond provider retention.",
                "backup,cloud",
                "Use vendor APIs to regularly export copies of SaaS data.",
            )
            mcq(
                "What is an audit trail used for when investigating data tampering?",
                [
                    "To block users from accessing the tampered data",
                    "To show who accessed or changed data and when",
                    "To encrypt evidence before reporting",
                    "To rotate backup tapes automatically",
                ],
                1,
                "Audit trails provide accountability and are essential for forensic investigations.",
                "audit,integrity",
                "Audit logs record user actions to reconstruct events during an investigation.",
            )
            mcq(
                "What differentiates a disaster recovery plan from a business continuity plan?",
                [
                    "DR plans focus on technology recovery; BC plans focus on keeping critical business functions running",
                    "DR plans focus on marketing campaigns; BC plans focus on IT only",
                    "They are identical and interchangeable",
                    "BC plans only apply after the DR plan completes",
                ],
                0,
                "DR emphasises restoring IT systems; BC focuses on maintaining or resuming critical business operations overall.",
                "disaster,bcp",
                "DR covers infrastructure recovery; BC covers broader business operations, including people/process.",
            )
            mcq(
                "Which environmental control reduces the risk of hardware damage from floods?",
                [
                    "Keeping cables unorganised and close to the floor",
                    "Placing equipment on raised racks and installing leak detectors",
                    "Turning off environmental monitoring to reduce alarms",
                    "Using only wireless networking gear",
                ],
                1,
                "Raised floors and leak detection help protect equipment from water ingress.",
                "environmental",
                "Raise equipment above the floor and use water sensors to detect leaks early.",
            )
            mcq(
                "Why is asset discovery/inventory important for data integrity?",
                [
                    "It ensures every asset has identical configuration",
                    "It tells you what must be protected, patched, monitored, or retired",
                    "It allows you to ignore legacy devices",
                    "It replaces the need for backups",
                ],
                1,
                "Inventory identifies hardware/software to apply updates, policies, and secure disposal.",
                "asset,inventory",
                "Keep an up-to-date inventory so no device is overlooked when patching or monitoring.",
            )
            mcq(
                "Which step is vital in the data disposal phase?",
                [
                    "Leaving drives intact so they can be reassigned quickly",
                    "Applying secure wipe or destruction so data cannot be recovered",
                    "Selling retired devices with all data intact to save costs",
                    "Ignorantly throwing away drives",
                ],
                1,
                "Secure wiping, physical destruction, or cryptographic erasure ensures data can't be recovered from retired media.",
                "disposal",
                "Wipe or destroy media securely before disposal.",
            )
            mcq(
                "What must be recorded when handling forensic evidence for admissibility?",
                [
                    "Just the final report with conclusions",
                    "Chain of custody showing who handled the evidence and when",
                    "Only the timestamp of the analysis",
                    "Nothing, as long as the evidence is preserved",
                ],
                1,
                "Documenting the chain of custody proves evidence wasn't tampered with during handling.",
                "forensics,chain",
                "Record every transfer or action performed on the evidence.",
            )
            mcq(
                "How can organisations keep production data available even after a disruption?",
                [
                    "By disabling backups to improve performance",
                    "By implementing BCP/DR plans with people, processes, and technology steps to recover critical services",
                    "By relying on a single backup tape stored locally without testing",
                    "By writing passwords on sticky notes for easy access",
                ],
                1,
                "BCP/DR planning identifies recovery priorities, manual workarounds, and communication plans.",
                "bcp,disaster",
                "Have documented recovery procedures and roles for restoring operations.",
            )
            mcq(
                "Why is complying with data classification important?",
                [
                    "It ensures every file is encrypted regardless of content",
                    "It ensures security controls match the sensitivity (e.g., public, official, secret)",
                    "It replaces the need for backups",
                    "It allows staff to delete data whenever they wish",
                ],
                1,
                "Classification guides handling, storage, communication, and retention based on sensitivity.",
                "classification,data",
                "Identify public vs sensitive data and apply appropriate controls.",
            )
            mcq(
                "Which activity demonstrates data integrity monitoring?",
                [
                    "Using checksums to verify files after copying or restoration",
                    "Backing up data without verifying restorability",
                    "Deleting backup logs every 24 hours",
                    "Allowing unrestricted write access to all staff",
                ],
                0,
                "Checksums compared before/after transfers confirm data was not altered.",
                "integrity",
                "Calculate and compare checksums to ensure files didn't change unintentionally.",
            )
            mcq(
                "What does a full backup include?",
                [
                    "Only files that have been modified since the last incremental backup",
                    "A complete copy of all selected data at that point in time",
                    "Only system state data including the registry and boot files",
                    "Only data that differs from the current differential baseline",
                ],
                1,
                "A full backup copies everything in the backup set, providing the simplest restore but taking the most time and space.",
                "backup",
                "A full backup creates a complete copy of all data in the backup set at that point in time.",
            )
            mcq(
                "What does an incremental backup capture?",
                [
                    "All data that has changed since the last full backup only",
                    "Only data that has changed since the last backup of any type",
                    "A complete copy of all data, but compressed to reduce storage",
                    "Only files that have been created new, excluding modified or deleted files",
                ],
                1,
                "Incremental backups save only changes since the last backup (full or incremental), making them fast but restore requires the chain.",
                "backup",
                "An incremental backup saves only the data that changed since the most recent backup of any kind.",
            )
            mcq(
                "How does a differential backup differ from an incremental?",
                [
                    "It captures changes since the last full backup, not since the last backup of any type",
                    "It captures only the changes since the most recent backup of any kind",
                    "It creates a full copy each time but stores only the unique data blocks",
                    "It backs up changes since the last incremental and merges them with the full",
                ],
                0,
                "Differential = changes since last full. Incremental = changes since last backup of any kind. Differential grows larger but restores faster.",
                "backup",
                "A differential backup captures everything that changed since the last full backup.",
            )
            mcq(
                "What is the Grandfather-Father-Son (GFS) backup rotation?",
                [
                    "A scheme using three full backups stored at three different offsite locations",
                    "A scheme using daily (son), weekly (father), and monthly (grandfather) backup cycles",
                    "A three-tier storage system: SSD for recent, HDD for medium-term, tape for archive",
                    "A rotation using three backup servers that alternate as primary each week",
                ],
                1,
                "GFS rotates backup media across daily, weekly, and monthly cycles to balance retention, cost, and recovery options.",
                "backup",
                "GFS is a backup rotation scheme: daily backups (son), weekly (father), and monthly (grandfather) for varied retention.",
            )
            mcq(
                "Why should backups be stored offsite or in the cloud?",
                [
                    "To ensure faster restore times by distributing data across multiple regions",
                    "To protect against site-wide disasters like fire, flood, or theft",
                    "To reduce the load on local storage systems during backup windows",
                    "To comply with data sovereignty laws that require geographic distribution",
                ],
                1,
                "Offsite storage ensures data survives even if the primary site is destroyed by a disaster.",
                "backup,disaster",
                "Offsite or cloud backup storage protects data from site-wide events that could destroy all local copies.",
            )
            mcq(
                "Why is restore testing critical for a backup strategy?",
                [
                    "It identifies which files have changed and need to be included in the next backup",
                    "It verifies that backups are usable and data can actually be recovered",
                    "It compresses backup archives to reclaim storage space on the backup server",
                    "It validates that the backup schedule aligns with the organisation's RPO targets",
                ],
                1,
                "Without restore testing you might discover too late that backups are corrupt, incomplete, or unusable.",
                "backup",
                "Restore testing confirms that backup data can actually be recovered successfully when needed.",
            )
            mcq(
                "What does RPO (Recovery Point Objective) measure?",
                [
                    "The maximum acceptable downtime before services must be restored",
                    "The maximum acceptable amount of data loss measured in time",
                    "The minimum number of backup copies that must be retained at all times",
                    "The target time to complete a full backup cycle of all systems",
                ],
                1,
                "RPO defines how much data (in time) you can afford to lose, e.g. RPO of 1 hour means max 1 hour of data loss.",
                "backup,disaster",
                "RPO is the maximum tolerable period of data loss, e.g. an RPO of 4 hours means you can lose at most 4 hours of data.",
            )
            mcq(
                "What does RTO (Recovery Time Objective) measure?",
                [
                    "The maximum tolerable amount of data loss measured in time",
                    "The maximum acceptable downtime before services must be restored",
                    "The frequency at which backups should be taken to meet recovery goals",
                    "The total time required to complete a full backup of all systems",
                ],
                1,
                "RTO defines the target time to restore operations after a disruption, e.g. RTO of 2 hours means systems must be up within 2 hours.",
                "backup,disaster",
                "RTO is the maximum tolerable downtime before systems and services must be restored after a disruption.",
            )
            mcq(
                "Why is RAID not a substitute for backups?",
                [
                    "RAID uses too much storage space compared to incremental backup strategies",
                    "RAID protects against drive failure but not accidental deletion, corruption, ransomware, or site disasters",
                    "RAID requires all disks to be the same brand and model, limiting flexibility",
                    "RAID cannot be used alongside a backup solution due to I/O conflicts",
                ],
                1,
                "RAID provides hardware redundancy (survives a disk failure) but does not protect against logical errors, malware, or site-level events.",
                "backup,raid",
                "RAID guards against disk failure only; it cannot protect against deletion, corruption, ransomware, or disasters.",
            )
            mcq(
                "What does RAID 1 (mirroring) do?",
                [
                    "Stripes data with parity across three or more disks for fault tolerance",
                    "Writes identical data to two or more disks for redundancy",
                    "Stripes data across disks without parity for improved read/write performance",
                    "Combines striping and mirroring using a minimum of four disks",
                ],
                1,
                "RAID 1 mirrors data across two drives so if one fails, the other has a complete copy.",
                "raid",
                "RAID 1 mirrors data by writing identical copies to two or more disks for hardware fault tolerance.",
            )
            mcq(
                "What does RAID 5 use to provide fault tolerance?",
                [
                    "Full mirroring of data between pairs of disks in the array",
                    "Distributed parity across all disks in the array",
                    "A dedicated hot spare disk that automatically replaces any failed drive",
                    "Striping without redundancy, relying on separate backups for data protection",
                ],
                1,
                "RAID 5 stripes data with distributed parity so the array can rebuild data if one disk fails.",
                "raid",
                "RAID 5 distributes parity information across all disks, allowing the array to survive one disk failure.",
            )
            mcq(
                "What is the purpose of a checksum?",
                [
                    "To encrypt data so it cannot be read by unauthorised parties",
                    "To verify data has not been altered by comparing a computed value",
                    "To compress data for more efficient storage and transmission",
                    "To authenticate the identity of the sender of a message",
                ],
                1,
                "A checksum is a value computed from data; if the data changes, the checksum will differ, indicating corruption or tampering.",
                "integrity",
                "A checksum is a computed value used to verify that data has not been modified or corrupted.",
            )
            mcq(
                "Why is audit logging important for data integrity?",
                [
                    "It encrypts sensitive data at rest to prevent unauthorised access",
                    "It records who did what and when, supporting accountability and incident investigation",
                    "It prevents users from making unauthorised changes by enforcing access controls",
                    "It automatically restores data to its original state if corruption is detected",
                ],
                1,
                "Audit logs provide a tamper-evident trail of actions, helping detect unauthorised changes and support forensic investigation.",
                "integrity,audit",
                "Audit logging records user actions and system events to support accountability and detect unauthorised changes.",
            )
            mcq(
                "What is the purpose of change control / change management?",
                [
                    "To restrict all changes to production systems unless authorised by senior management alone",
                    "To ensure changes are reviewed, approved, tested, and documented before implementation",
                    "To automate the deployment of patches and updates without manual intervention",
                    "To maintain a complete backup of every system state before and after each change",
                ],
                1,
                "Change control ensures modifications are deliberate, approved, and reversible, reducing the risk of unplanned outages or data loss.",
                "integrity",
                "Change management ensures that all changes are reviewed, approved, tested, and documented to minimise risk.",
            )
            mcq(
                "Which environmental threat can a fire suppression system protect against?",
                [
                    "Water damage from burst pipes or rising floodwater",
                    "Fire destroying hardware and data in the server room",
                    "Overheating caused by air conditioning failure",
                    "Power surges from lightning strikes or grid instability",
                ],
                1,
                "Fire suppression systems (gas-based or sprinkler) protect equipment and data from fire damage.",
                "environmental",
                "Fire suppression systems detect and extinguish fires to protect hardware, media, and data in server rooms.",
            )
            mcq(
                "What control helps protect a server room from flooding?",
                [
                    "Gas-based fire suppression systems like FM-200 or Novec 1230",
                    "Raised flooring, water sensors, and locating equipment above ground level",
                    "Uninterruptible power supplies (UPS) with surge protection",
                    "Biometric access controls and CCTV monitoring at entry points",
                ],
                1,
                "Raised floors, leak sensors, and proper site selection minimise flood risk to IT equipment.",
                "environmental",
                "Raised flooring, water detection sensors, and above-ground placement help protect servers from flood damage.",
            )
            mcq(
                "What does a UPS (Uninterruptible Power Supply) protect against?",
                [
                    "Hardware failure caused by disk degradation over time",
                    "Short-term power outages and surges, giving time for safe shutdown or generator start",
                    "Overheating by providing supplemental cooling to server racks",
                    "Flooding damage from burst pipes or rising water levels",
                ],
                1,
                "A UPS provides battery backup so systems can shut down gracefully or stay running until a generator takes over.",
                "environmental",
                "A UPS provides battery power during outages to allow graceful shutdown or bridge to generator power.",
            )
            mcq(
                "Why should server room temperature be monitored?",
                [
                    "Low humidity causes static discharge that can damage sensitive components",
                    "Overheating causes hardware failure and data loss; monitoring triggers alerts before damage occurs",
                    "Cold temperatures slow down CPU processing and reduce server performance",
                    "Temperature fluctuations indicate potential security breaches via the HVAC system",
                ],
                1,
                "Excessive heat damages components and reduces lifespan; environmental monitoring with alerts prevents unplanned outages.",
                "environmental",
                "High temperatures cause hardware failure; environmental monitoring triggers alerts before damage occurs.",
            )
            mcq(
                "What does the Australian Privacy Act 1988 primarily regulate?",
                [
                    "How organisations must implement cybersecurity controls for critical infrastructure",
                    "How organisations collect, use, store, and disclose personal information",
                    "How personal data must be encrypted during storage and transmission",
                    "How organisations report financial data to regulatory authorities",
                ],
                1,
                "The Privacy Act governs the handling of personal information by Australian government agencies and private organisations.",
                "privacy",
                "The Privacy Act 1988 governs how Australian organisations handle personal information.",
            )
            mcq(
                "What are the Australian Privacy Principles (APPs)?",
                [
                    "A set of mandatory cybersecurity standards for all Australian businesses",
                    "13 principles that outline how personal information must be handled under the Privacy Act",
                    "A framework for classifying data sensitivity levels in government agencies",
                    "Legally required data breach notification procedures for critical infrastructure",
                ],
                1,
                "The 13 APPs cover collection, use, disclosure, quality, security, access, and correction of personal information.",
                "privacy",
                "The 13 APPs set out standards for handling personal information under the Australian Privacy Act.",
            )
            mcq(
                "In a risk assessment, what does 'likelihood' refer to?",
                [
                    "The potential damage or consequence if a threat event occurs",
                    "The probability that a threat will exploit a vulnerability",
                    "The monetary value of the asset that is being protected from threats",
                    "The number of known vulnerabilities currently present in the system",
                ],
                1,
                "Likelihood estimates how probable it is that a given threat will occur and exploit a vulnerability.",
                "risk",
                "Likelihood is the estimated probability that a specific threat will occur and successfully exploit a vulnerability.",
            )
            mcq(
                "How is risk typically calculated in a basic risk matrix?",
                [
                    "Risk = Threat x Vulnerability x Asset Value",
                    "Risk = Likelihood x Impact",
                    "Risk = Impact divided by Likelihood",
                    "Risk = Number of Vulnerabilities x Cost of Mitigation",
                ],
                1,
                "Risk = Likelihood x Impact. High likelihood and high impact = highest priority risk.",
                "risk",
                "A risk matrix plots likelihood against impact to prioritise risks: Risk = Likelihood x Impact.",
            )
            mcq(
                "What is the purpose of a disaster recovery plan (DRP)?",
                [
                    "To identify and eliminate all potential threats before they cause disruption",
                    "To define procedures for restoring IT systems and data after a major disruption",
                    "To ensure the organisation can continue operations during a disruption without any downtime",
                    "To document the organisation's risk appetite and acceptable levels of residual risk",
                ],
                1,
                "A DRP documents step-by-step procedures to recover critical systems and resume operations after a disaster.",
                "disaster",
                "A disaster recovery plan outlines procedures to restore IT services and data after a major disruptive event.",
            )
            mcq(
                "What is a rollback procedure?",
                [
                    "Applying a hotfix to resolve issues introduced by a recent change",
                    "Reverting a system or data to a previous known-good state after a failed change",
                    "Performing a full system restore from the most recent backup after data loss",
                    "Gradually migrating services to new infrastructure while decommissioning the old",
                ],
                1,
                "Rollback undoes a change that caused problems, restoring the system to its previous stable state.",
                "integrity,disaster",
                "A rollback procedure reverts a system or dataset to a previous known-good state after a problematic change.",
            )
            mcq(
                "What does physical access control to a server room typically involve?",
                [
                    "Firewalls and intrusion detection systems monitoring network traffic",
                    "Locked doors, key cards or biometrics, visitor logs, and CCTV",
                    "Encryption of all data stored on servers within the room",
                    "Role-based access control policies applied to network file shares",
                ],
                1,
                "Physical access controls restrict who can enter sensitive areas using locks, badges, biometrics, and surveillance.",
                "access,environmental",
                "Physical access control uses locks, key cards, biometrics, visitor logs, and CCTV to restrict server room entry.",
            )

            # Data classification and handling
            mcq(
                "What is the main purpose of a data classification scheme?",
                [
                    "To reduce storage costs by deleting older data",
                    "To categorise data by sensitivity and impact so appropriate controls can be applied",
                    "To ensure all data is kept forever for legal reasons",
                    "To identify which files should be compressed for backup",
                ],
                1,
                "Classification (e.g. public, internal, confidential) drives which security controls and handling rules are required.",
                "classification,integrity",
                "You cannot protect data properly if you don't know how sensitive it is.",
            )
            mcq(
                "Which of the following is the BEST example of handling 'confidential' data?",
                [
                    "Sending it via unencrypted email to external addresses",
                    "Storing it only on encrypted company devices and sharing via approved secure channels",
                    "Copying it to personal USB drives for convenience",
                    "Uploading it to any free cloud storage service for backup",
                ],
                1,
                "Confidential data should remain on controlled, encrypted systems and be transmitted only over secure channels.",
                "classification,privacy",
                "Think about where the data lives, who can access it, and how it's transmitted.",
            )

            # Data Loss Prevention (DLP)
            mcq(
                "What is the primary goal of a Data Loss Prevention (DLP) solution?",
                [
                    "To automatically encrypt all data at rest",
                    "To detect and prevent unauthorised transmission or storage of sensitive data",
                    "To compress large files before they are emailed",
                    "To track how much bandwidth users consume",
                ],
                1,
                "DLP tools inspect data in motion/at rest to stop sensitive information leaving in unauthorised ways.",
                "dlp,integrity",
                "DLP policies are usually based on data classification and patterns (e.g. credit card numbers).",
            )
            mcq(
                "Which scenario best illustrates the use of DLP on email?",
                [
                    "Blocking all attachments larger than 10 MB",
                    "Scanning outbound emails for patterns like credit card or tax file numbers and blocking or encrypting them",
                    "Deleting all emails older than 30 days",
                    "Automatically adding a legal disclaimer to every message",
                ],
                1,
                "DLP inspects email content/attachments and takes action when sensitive data patterns are detected.",
                "dlp,privacy",
                "Common DLP actions include block, encrypt, or notify.",
            )

            # Business continuity and DRP
            mcq(
                "How does a Business Continuity Plan (BCP) differ from a Disaster Recovery Plan (DRP)?",
                [
                    "A BCP focuses only on IT systems; a DRP covers the whole business",
                    "A BCP focuses on keeping critical business functions running; a DRP focuses on restoring IT systems and data",
                    "A BCP is optional while a DRP is mandatory under all regulations",
                    "A BCP is purely technical; a DRP is purely administrative",
                ],
                1,
                "BCP = keep business processes operating (people, facilities, workarounds). DRP = restore IT systems and data.",
                "business_continuity,disaster",
                "Think: 'keep operating' vs 'restore systems'. Both are needed.",
            )
            mcq(
                "Which of the following is MOST important when defining BCP priorities?",
                [
                    "The age of the hardware running each application",
                    "The revenue, regulatory, and safety impact if a process is unavailable",
                    "The number of users who have complained about the system in the past",
                    "The vendor support contract expiry date",
                ],
                1,
                "BCP prioritisation is based on business impact (financial, legal, safety, reputation), not just technical details.",
                "business_continuity,risk",
                "High-impact processes get stricter RPO/RTO and more robust continuity arrangements.",
            )

            # Encryption at rest / integrity
            mcq(
                "What does 'encryption at rest' mean in the context of data integrity and security?",
                [
                    "Data is encrypted only while it is being transmitted over the network",
                    "Data stored on disks or other media is encrypted, reducing impact if storage is lost or stolen",
                    "Data is compressed before being written to disk to save space",
                    "Data is digitally signed before transmission",
                ],
                1,
                "Encryption at rest protects confidentiality if disks or backups are accessed without authorisation.",
                "crypto,integrity",
                "It does not replace backups or access control, but complements them.",
            )
            mcq(
                "Which control BEST helps ensure the integrity of backups stored offsite?",
                [
                    "Encrypting backup media with strong algorithms",
                    "Using checksums or hashes to verify backup files have not been altered or corrupted",
                    "Storing backups in multiple geographic locations",
                    "Compressing backups to reduce storage requirements",
                ],
                1,
                "Checksums/hashes detect changes; encryption protects confidentiality, not integrity alone.",
                "backup,integrity",
                "Integrity = ability to detect unauthorised or accidental change.",
            )

            # Scenario-based integrity / backup questions
            mcq(
                "A company has an RPO of 4 hours and performs only a full backup every night at 2am. Which statement is TRUE?",
                [
                    "The RPO is met because a daily full backup is always sufficient",
                    "The RPO is not met; up to almost 24 hours of data could be lost if a failure occurs before the next backup",
                    "The RPO is met if RAID is also used on the storage system",
                    "The RPO does not apply to backup strategies, only to network availability",
                ],
                1,
                "With only nightly full backups, you can lose up to nearly a full day of data, violating a 4‑hour RPO.",
                "backup,risk",
                "Meeting low RPOs usually requires more frequent backups or replication.",
            )
            mcq(
                "A ransomware attack encrypts all data on a file server at 3pm. The last good backup finished at 1pm, and backups run hourly. Which requirement does this help meet?",
                [
                    "A low RTO by allowing instant failover to a secondary site",
                    "A 2‑hour RPO by limiting data loss to about 2 hours of changes",
                    "A long-term retention requirement of 7 years",
                    "A requirement for encryption at rest",
                ],
                1,
                "Hourly backups limit data loss to roughly an hour; here the 2‑hour window is met.",
                "backup,disaster",
                "Frequent backups or snapshots are key to surviving ransomware with minimal data loss.",
            )

            # Scenario-based access / audit / change control
            mcq(
                "After a change to a database, users report data corruption in a key table. Which combination of controls would BEST help identify the cause and recover?",
                [
                    "Audit logging and a documented change management process with rollback steps",
                    "Periodic password changes and stricter screen lock settings",
                    "Content filtering on the internet proxy and email gateway",
                    "Increased Wi‑Fi coverage and bandwidth in the office",
                ],
                0,
                "Audit logs plus structured change control and rollback procedures allow you to trace who changed what and revert safely.",
                "audit,integrity,disaster",
                "Good change management always includes testing, approvals, and rollback plans.",
            )
            mcq(
                "A security review finds that administrators are making urgent production changes without approvals or documentation. Which RISK is most increased?",
                [
                    "Loss of confidentiality of backup data",
                    "Unplanned outages and data integrity issues due to uncontrolled changes",
                    "Increased spam volume entering user mailboxes",
                    "Inability to restore from backups after a disaster",
                ],
                1,
                "Uncontrolled changes are a common source of outages and silent data corruption.",
                "integrity,risk",
                "Change control exists to reduce the risk of breaking systems or corrupting data.",
            )

        cur.executemany(
            """
            INSERT INTO quiz_questions (unit_id, q_type, question, choices_json, answer_index, explanation, tags, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
            qs,
        )

    # Persist quiz seed version so we don't re-seed unnecessarily
    if quiz_version_changed:
        cur.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", ("quiz_seed_version", QUIZ_SEED_VERSION)
        )

    # ─── Seed short answer questions ──────────────────────────────
    EXPECTED_SA_PER_UNIT = 30  # target ~30 SA questions per unit
    SA_SEED_VERSION = "1"  # v1: expanded SA bank with scenarios

    cur.execute("SELECT value FROM settings WHERE key = 'sa_seed_version';")
    sa_row = cur.fetchone()
    sa_version_changed = (sa_row is None) or (sa_row["value"] != SA_SEED_VERSION)
    for ucode in ("ICTNWK421", "ICTNWK423"):
        u = cur.execute("SELECT id FROM units WHERE code = ?;", (ucode,)).fetchone()
        if not u:
            continue
        unit_id = int(u["id"])

        cur.execute("SELECT COUNT(*) AS n FROM short_answer_questions WHERE unit_id = ?;", (unit_id,))
        if cur.fetchone()["n"] >= EXPECTED_SA_PER_UNIT and not sa_version_changed:
            continue

        cur.execute("DELETE FROM short_answer_questions WHERE unit_id = ?;", (unit_id,))

        sa_qs = []

        def sa(question, model_answer, explanation, tags="", context=""):
            sa_qs.append((unit_id, question.strip(), model_answer.strip(), explanation.strip(), tags, context.strip()))

        # Shared questions (both units)
        sa(
            "Explain the principle of least privilege and give two network examples.",
            "Least privilege means giving users and services only the minimum access they need to do their job. Example 1: restricting admin access to a management VLAN only. Example 2: allowing only required ports (e.g. 80, 443) through the firewall to a web server.",
            "The key idea is minimum necessary access; examples should be concrete network scenarios.",
            "principles",
            "Think about what happens if an account is compromised — less privilege means less damage.",
        )
        sa(
            "What is the difference between hashing and encryption? What does each provide?",
            "Hashing is a one-way function that produces a fixed-size digest from data; it provides integrity verification (you can detect if data has changed). Encryption is a two-way process using a key to make data unreadable; it provides confidentiality (only authorised parties can read the data).",
            "Hashing = integrity (one-way, detect change). Encryption = confidentiality (two-way, protect content).",
            "crypto",
            "Hashing cannot be reversed; encryption can be reversed with the correct key.",
        )
        sa(
            "Why is an IDS not a replacement for a firewall? Explain what each does.",
            "A firewall filters traffic based on rules (allow/deny) and acts as a gatekeeper at network boundaries. An IDS monitors traffic passively and alerts when it detects suspicious patterns, but it does not block traffic. They serve complementary roles: the firewall enforces policy, while the IDS detects threats that may bypass the firewall.",
            "Firewall = enforce rules (block/allow). IDS = detect and alert. They complement each other.",
            "ids,firewall",
            "An IDS detects suspicious activity; a firewall enforces traffic rules.",
        )
        sa(
            "Describe the purpose of multi-factor authentication (MFA) and name the three factor types.",
            "MFA requires users to prove their identity using two or more different factor types, making it much harder for attackers to gain access. The three factor types are: something you know (password, PIN), something you have (phone, token, smart card), and something you are (fingerprint, face scan, biometric).",
            "MFA = two or more from different categories: knowledge, possession, biometric.",
            "access,mfa",
            "Using two passwords is NOT MFA because both are the same factor type (knowledge).",
        )

        if ucode == "ICTNWK421":
            sa(
                "Compare a stateful firewall with a stateless firewall. When would you choose each?",
                "A stateful firewall tracks the state of active connections (new, established, related) and automatically allows legitimate return traffic. A stateless firewall evaluates each packet independently against static rules. Stateful is preferred for most networks because it is more secure and easier to manage. Stateless may be used on very simple or high-throughput devices where performance is critical and rules are straightforward.",
                "Stateful tracks connections; stateless checks each packet alone. Stateful is generally preferred.",
                "firewall",
                "Stateful inspection remembers whether a connection was initiated from inside or outside the network.",
            )
            sa(
                "What is a DMZ and why is it used in network architecture?",
                "A DMZ (demilitarised zone) is an isolated network segment placed between the internal LAN and the external internet, typically using two firewalls. Public-facing servers (web, email, DNS) are placed in the DMZ so that if they are compromised, the attacker does not have direct access to the internal network. It adds a layer of defence in depth.",
                "DMZ = isolated zone for public servers, protecting the internal network from direct exposure.",
                "firewall,principles",
                "A DMZ sits between the internet and the internal network, usually separated by firewalls on both sides.",
            )
            sa(
                "Explain VPN tunnelling and why encryption is essential for VPN security.",
                "VPN tunnelling encapsulates private network packets inside public network packets, allowing them to travel securely across an untrusted network like the internet. Encryption is essential because without it, the encapsulated data could be intercepted and read by anyone who captures the packets. Together, tunnelling and encryption provide a secure private channel over a public network.",
                "Tunnelling = encapsulation of private packets inside public ones. Encryption stops eavesdropping.",
                "vpn,crypto",
                "Think of tunnelling as putting a letter inside a sealed envelope that travels through public mail.",
            )
            sa(
                "What is DNS cache poisoning and how can it be prevented?",
                "DNS cache poisoning is an attack where false DNS records are injected into a resolver's cache, causing users to be redirected to malicious websites. Prevention measures include: using DNSSEC (which cryptographically signs DNS responses), randomising source ports and transaction IDs for DNS queries, keeping DNS software patched, and using trusted DNS resolvers.",
                "Poisoning = fake DNS records redirect users. Prevent with DNSSEC, patching, and randomised queries.",
                "dns,threats",
                "DNS cache poisoning tricks DNS resolvers into storing incorrect IP addresses for domain names.",
            )
            sa(
                "Explain the difference between a penetration test and a vulnerability scan.",
                "A vulnerability scan is an automated tool that checks systems for known weaknesses (missing patches, misconfigurations) and produces a report. A penetration test goes further: a skilled tester actively tries to exploit vulnerabilities to see how far an attacker could get. Pen tests simulate real attacks and test defences in depth, while vulnerability scans are broader but shallower.",
                "Vuln scan = automated check for known weaknesses. Pen test = manual exploitation to test real-world impact.",
                "audit,testing",
                "Vulnerability scans find potential issues; penetration tests prove whether they can actually be exploited.",
            )
            sa(
                "Why is SSH preferred over Telnet for remote administration? Describe the key security difference.",
                "SSH encrypts the entire session (including credentials, commands, and output) using strong cryptography, so data cannot be read if intercepted. Telnet sends everything in plaintext, meaning anyone capturing network traffic can see passwords and commands. SSH also supports key-based authentication for even stronger security.",
                "SSH = encrypted session. Telnet = plaintext. SSH prevents eavesdropping on credentials and commands.",
                "ssh,telnet",
                "SSH uses encryption; Telnet does not. This is the critical security difference.",
            )
            sa(
                "What does 'defence in depth' mean? Give three examples of different security layers.",
                "Defence in depth means using multiple overlapping layers of security so that if one control fails, others still protect the system. Examples: (1) a perimeter firewall filtering external traffic, (2) an IDS/IPS monitoring internal network segments for suspicious activity, (3) endpoint antivirus software on each workstation, (4) strong access controls with MFA, (5) regular patching and audit logging.",
                "Multiple independent layers of security; no single point of failure. Examples should span different control types.",
                "principles",
                "Think physical, network, host, application, and administrative controls.",
            )
            sa(
                "What is a man-in-the-middle (MITM) attack and how can it be prevented?",
                "A MITM attack occurs when an attacker secretly intercepts and potentially alters communication between two parties who believe they are communicating directly. Prevention includes: using encrypted protocols (HTTPS, SSH, VPN), verifying certificates, implementing MFA, and using secure DNS. Network controls like 802.1X and DHCP snooping also help prevent MITM at the network level.",
                "MITM = attacker intercepts communication. Prevent with encryption, certificate verification, and network controls.",
                "threats",
                "The attacker positions themselves between two communicating parties without either knowing.",
            )

            # Additional ICTNWK421 short answer questions — wireless, VLANs, PKI, incident response
            sa(
                "Describe how 802.1X improves security on a corporate Wi‑Fi network.",
                "802.1X provides port-based network access control. On Wi‑Fi it is usually combined with WPA2/WPA3-Enterprise so each user authenticates (e.g. via username/password or certificate) against a RADIUS server before getting full network access. This means credentials are individual, centrally managed, and can be revoked, and unauthenticated devices are kept on a limited or guest network.",
                "Key ideas: port-based access control, per-user authentication, integration with RADIUS, preventing unauthorised devices from joining the LAN.",
                "wireless,access",
                "Think about the difference between a shared pre‑shared key and per-user credentials when staff leave.",
            )
            sa(
                "What is a rogue access point and how would you detect and respond to one?",
                "A rogue access point is an unauthorised wireless AP connected to the network (or mimicking it) that bypasses normal security controls. Detection methods include: wireless surveys and scans to find unknown SSIDs/BSSIDs, monitoring switch ports for unauthorised MAC addresses, and using wireless intrusion detection systems. Response: locate and physically remove or disable the AP, investigate who installed it, and tighten policies and technical controls to prevent recurrence.",
                "Define rogue AP, describe at least one technical detection method, and outline a basic response (locate, remove, investigate, prevent).",
                "wireless,threats",
                "Many rogue APs are just 'convenience' devices staff plug into wall ports.",
            )
            sa(
                "Explain why VLANs are used for network segmentation and give two examples of useful VLANs in a small organisation.",
                "VLANs segment a switched network into separate broadcast domains so that traffic is logically separated even on the same physical switches. This limits broadcast noise and, more importantly, supports security zoning when combined with routing and ACLs. Example VLANs: (1) A 'Server' VLAN where file/database servers live, with tight rules about which user VLANs can access them; (2) A 'Guest Wi‑Fi' VLAN that has only internet access and no access to internal systems.",
                "Answer should cover the concept of logical segmentation, reduced lateral movement, and at least two concrete VLAN examples.",
                "vlan,segmentation",
                "Think of VLANs as virtual separate switches sharing the same hardware.",
            )
            sa(
                "You are asked to design segmentation for a small office: staff PCs, servers, and guest Wi‑Fi. Propose a simple VLAN layout and access rules.",
                "One simple design: VLAN 10 Staff, VLAN 20 Servers, VLAN 30 Guest Wi‑Fi. Staff VLAN can access required server ports (e.g. SMB, HTTP/HTTPS to internal apps). Guest VLAN is routed only to the internet and blocked from VLAN 10 and 20. Management interfaces for switches/firewalls are reachable only from a secure admin subnet or via VPN. Inter‑VLAN ACLs or firewall rules enforce these policies.",
                "Look for clear VLAN IDs, which devices go in each VLAN, and high‑level access rules that block guests from internal resources.",
                "vlan,firewall",
                "Keep management access separate from normal user and guest traffic.",
            )
            sa(
                "What role does a Certificate Authority (CA) play in PKI, and why is it important for HTTPS and VPNs?",
                "A CA is a trusted third party that issues digital certificates binding a public key to an identity (such as a DNS name or organisation). Browsers and VPN clients trust a set of root CAs; if a server presents a certificate signed by one of these (or a trusted intermediate), the client can verify it is talking to the genuine server and not an impersonator. Without trusted CAs, it would be much harder to prevent man‑in‑the‑middle attacks.",
                "Explain 'trusted third party', binding keys to identities, and why clients rely on CA trust stores for HTTPS/VPN validation.",
                "pki,crypto",
                "Think of CAs as the 'ID card issuers' on the internet.",
            )
            sa(
                "Explain why ignoring browser certificate warnings can be dangerous in a corporate environment.",
                "Certificate warnings can indicate that the certificate is expired, misconfigured, or not trusted, but they can also indicate a man‑in‑the‑middle (MITM) attack where someone is intercepting traffic and presenting their own certificate. If users routinely bypass these warnings, attackers can more easily capture credentials or sensitive data by spoofing internal or external sites.",
                "Key points: certificate warnings may signal MITM; training users to ignore them undermines TLS security.",
                "pki,threats",
                "Corporate policy should define when and how certificate issues are investigated.",
            )
            sa(
                "Outline the main phases of an incident response process.",
                "A common model has these phases: (1) Preparation – policies, tools, training, logging. (2) Identification – detect and confirm the incident, determine scope and type. (3) Containment – limit spread/damage while preserving evidence. (4) Eradication – remove root cause (malware, misconfigurations, compromised accounts). (5) Recovery – restore systems to normal operation, monitor for recurrence. (6) Lessons learned – review what happened and improve controls and procedures.",
                "Look for at least four of the phases and a brief description of each.",
                "incident",
                "Many frameworks (e.g. NIST) use similar phase names; exact wording can vary.",
            )
            sa(
                "Give an example of a short-term containment action and a longer-term eradication action for a malware infection on a workstation.",
                "Short-term containment: disconnect the workstation from the network or isolate it on a quarantine VLAN to stop malware spreading while preserving logs. Longer-term eradication: remove the malware by reimaging the system from a trusted image, applying patches, resetting credentials, and verifying with AV/EDR scans.",
                "Containment = quick isolation to limit damage; eradication = thorough removal and hardening.",
                "incident,threats",
                "Containment should avoid destroying useful forensic evidence where possible.",
            )
            sa(
                "Describe what should be included in an incident report after a security incident is resolved.",
                "An incident report should include: timeline of events, systems and data affected, root cause, how the incident was detected, actions taken during containment/eradication/recovery, impact (technical and business), lessons learned, and follow‑up actions (e.g. additional controls, training, policy updates). It should be factual and clear enough for management and auditors.",
                "Emphasise timeline, impact, root cause, actions taken, and lessons learned/follow‑ups.",
                "incident,audit",
                "Good reports support accountability and future improvements, not blame.",
            )
            sa(
                "Explain how network monitoring tools (such as SNMP-based monitoring) can support incident detection and troubleshooting.",
                "Network monitoring tools collect metrics and alerts from devices (CPU, memory, interface errors, bandwidth, link status) via protocols like SNMP. Sudden changes – such as spikes in traffic, high error rates, or unexpected interface flapping – can indicate faults or attacks (e.g. DoS, misconfigurations). Historical graphs help correlate events and speed up root-cause analysis during incidents.",
                "Connect monitoring metrics to early detection and faster troubleshooting of both faults and security events.",
                "monitoring,incident",
                "Monitoring is part of 'preparation' in incident response.",
            )
            sa(
                "A user reports that they connected to the office Wi‑Fi and saw a certificate warning when accessing the intranet. What steps should you take?",
                "First, advise the user not to proceed past the warning. Verify the URL and compare the certificate presented with the expected certificate (issuer, subject, fingerprint). Check if there have been recent certificate renewals or proxy changes. Investigate whether there might be a rogue access point or transparent proxy intercepting traffic. Only once the cause is identified and fixed should users be told it is safe to proceed.",
                "Answer should avoid 'click through' and instead focus on verification, checking for misconfiguration versus possible MITM, and communicating clearly with users.",
                "pki,wireless,incident",
                "This ties together Wi‑Fi, PKI, and incident response thinking.",
            )

        if ucode == "ICTNWK423":
            sa(
                "Compare full, incremental, and differential backups. When would you use each?",
                "A full backup copies all selected data — simplest to restore but slowest and uses most storage. An incremental backup saves only data changed since the last backup of any type — fastest and smallest, but restore requires the full backup plus every incremental in sequence. A differential backup saves changes since the last full backup — larger than incremental but faster to restore (only need the full + latest differential).",
                "Full = everything. Incremental = changes since last backup. Differential = changes since last full.",
                "backup",
                "Consider restore time vs backup time vs storage space when choosing a strategy.",
            )
            sa(
                "Explain RPO and RTO. Why are they important for disaster recovery planning?",
                "RPO (Recovery Point Objective) is the maximum acceptable amount of data loss, measured in time (e.g. RPO of 4 hours means you can lose at most 4 hours of data). RTO (Recovery Time Objective) is the maximum acceptable downtime before services must be restored. They are important because they determine backup frequency (RPO) and recovery infrastructure requirements (RTO), directly affecting cost and business continuity.",
                "RPO = max data loss. RTO = max downtime. They drive backup frequency and recovery design.",
                "backup,disaster",
                "Low RPO requires frequent backups; low RTO requires fast recovery infrastructure.",
            )
            sa(
                "Why is RAID not a substitute for backups? Explain with examples.",
                "RAID provides hardware redundancy — if a disk fails, the array continues operating. However, RAID does not protect against: accidental file deletion (RAID mirrors the deletion instantly), ransomware (encrypts files on all RAID disks), data corruption (corrupted data is mirrored/striped), or site-wide disasters (fire, flood destroy all disks). Backups provide a separate, recoverable copy of data from a point in time.",
                "RAID handles disk failure only. Backups protect against deletion, corruption, ransomware, and site disasters.",
                "backup,raid",
                "RAID is about availability; backups are about recovery.",
            )
            sa(
                "What is the purpose of audit logging and how does it support data integrity?",
                "Audit logging records who did what, when, and to which resources. It supports data integrity by: providing accountability (users know actions are recorded), enabling detection of unauthorised changes, supporting incident investigation and forensic analysis, and demonstrating compliance with policies and regulations. Logs should be tamper-resistant and stored securely.",
                "Audit logs = who, what, when. Supports accountability, detection, investigation, and compliance.",
                "integrity,audit",
                "Audit logs should be protected from modification to maintain their evidentiary value.",
            )
            sa(
                "Describe two environmental threats to a data centre and one control for each.",
                "Threat 1: Fire — can destroy hardware, media, and data. Control: gas-based fire suppression system (e.g. FM-200) that extinguishes fire without water damage, plus smoke detectors for early warning. Threat 2: Flooding — water damage to servers and electrical systems. Control: raised flooring, water detection sensors, and locating the data centre above ground level to minimise flood risk.",
                "Name specific threats and matched controls. Environmental threats include fire, flood, heat, and power failure.",
                "environmental",
                "Think about what could physically damage equipment and what controls mitigate each threat.",
            )
            sa(
                "What does the Australian Privacy Act 1988 require organisations to do regarding personal information?",
                "The Privacy Act 1988 requires organisations to follow the 13 Australian Privacy Principles (APPs) when handling personal information. This includes: collecting only necessary information, being transparent about how it is used, storing it securely, allowing individuals to access and correct their data, and not disclosing it without consent or lawful reason. Breaches must be reported under the Notifiable Data Breaches scheme.",
                "Follow the 13 APPs: collect fairly, store securely, allow access/correction, report breaches.",
                "privacy",
                "The Privacy Act covers Australian government agencies and private organisations above the revenue threshold.",
            )
            sa(
                "Explain the change management process and why it is important for data integrity.",
                "Change management is a structured process for making changes to IT systems: (1) submit a change request, (2) assess risk and impact, (3) get approval, (4) test in a non-production environment, (5) implement with a rollback plan, (6) document and review. It protects data integrity by preventing unplanned changes that could cause outages, data loss, or security holes.",
                "Structured process: request, assess, approve, test, implement, review. Prevents unplanned damage to systems and data.",
                "integrity",
                "Change management reduces the risk of errors by ensuring changes are reviewed and reversible.",
            )
            sa(
                "What is a rollback procedure and when would you use one?",
                "A rollback procedure reverts a system or data to a previous known-good state after a change causes problems. You would use it when: a software update introduces bugs, a configuration change breaks services, a database migration corrupts data, or a patch causes compatibility issues. Rollback relies on having backups, snapshots, or version control to restore the prior state.",
                "Rollback = revert to previous good state. Used when changes cause failures or data issues.",
                "integrity,disaster",
                "Always have a rollback plan before making changes to production systems.",
            )
            sa(
                "How does risk assessment work? Describe the basic steps and the risk calculation.",
                "Risk assessment identifies and prioritises threats to an organisation. Steps: (1) identify assets (what needs protecting), (2) identify threats and vulnerabilities, (3) assess likelihood (probability of occurrence) and impact (damage if it occurs), (4) calculate risk using Risk = Likelihood x Impact, (5) prioritise and decide on treatment (accept, mitigate, transfer, avoid). A risk matrix helps visualise priorities.",
                "Identify assets and threats, assess likelihood and impact, calculate Risk = Likelihood x Impact, then prioritise.",
                "risk",
                "Risk = Likelihood x Impact. High values in both = highest priority to address.",
            )

            # Additional ICTNWK423 short answer questions — classification, DLP, BCP
            sa(
                "Define data classification and give an example of a simple classification scheme for an organisation.",
                "Data classification is the process of labelling information based on its sensitivity and the impact if it is disclosed, changed, or lost. A simple scheme could have four levels: Public (can be shared with anyone), Internal (for staff only), Confidential (limited staff with a business need), and Highly Confidential (very restricted, such as financials or personal information). Each level then has handling rules (where it can be stored, how it is transmitted, who can access it).",
                "Look for the idea of categories based on sensitivity/impact and at least one example scheme with handling implications.",
                "classification,privacy",
                "Classification drives which technical and procedural controls must be used.",
            )
            sa(
                "How does data classification support compliance with privacy legislation like the Australian Privacy Act 1988?",
                "Privacy legislation requires organisations to protect personal information appropriately. Classification helps by clearly labelling which data sets contain personal or highly sensitive information so stronger controls (encryption, access restrictions, DLP rules, stricter logging) can be applied. It also helps ensure that personal data is only used, stored, and shared in ways consistent with policies and legal requirements.",
                "Key link: classification identifies personal/sensitive data so you can apply appropriate privacy controls and monitor its use.",
                "classification,privacy",
                "Without knowing where personal data lives, it's hard to protect or prove compliance.",
            )
            sa(
                "Explain what a Data Loss Prevention (DLP) system does and give one example of a rule it might enforce.",
                "A DLP system monitors data in use, in motion, and at rest to detect and stop unauthorised transfer or storage of sensitive information. For example, a DLP rule could scan outgoing emails for patterns matching tax file numbers or credit card numbers; if detected, it could block the email, encrypt it, or require additional approval before sending.",
                "Answer should describe monitoring and blocking/controlling sensitive data flows, plus a concrete example rule.",
                "dlp,integrity",
                "DLP systems rely heavily on good classification and pattern definitions.",
            )
            sa(
                "Describe the difference between Business Continuity Planning (BCP) and Disaster Recovery Planning (DRP) using a practical example.",
                "BCP is about keeping critical business functions running during and after a disruption, often via workarounds. DRP is about restoring IT systems and data. For example, after a data centre fire: BCP might specify that customer service staff work from a secondary office with manual processes and limited systems; DRP describes how to rebuild servers, restore backups, and switch users back to normal applications.",
                "Look for an explanation that BCP is business-process focused while DRP is IT-system focused, plus a short scenario.",
                "business_continuity,disaster",
                "BCP often involves people, locations, suppliers, and alternative processes.",
            )
            sa(
                "An organisation has defined an RTO of 4 hours for its main customer database. What does this mean, and how might it influence technology choices?",
                "An RTO of 4 hours means the organisation aims to restore the customer database and make it available again within 4 hours of a disruption. To meet this, they may need technologies like clustered databases, warm standby instances, high‑speed storage, and well‑rehearsed recovery procedures. Purely manual rebuilds from tape backups are unlikely to meet the target.",
                "Explain RTO in time-to-recover terms and link it to technology/infrastructure and process decisions.",
                "disaster,risk",
                "Lower RTOs generally mean more cost and complexity in the recovery solution.",
            )
            sa(
                "Why is it important to regularly test backup restores rather than assuming backups are working?",
                "Backups can quietly fail or be incomplete due to configuration errors, storage problems, or software bugs. Until you actually restore and verify data, you don't know whether the backups are usable. Regular restore testing proves that data can be recovered within the required RPO/RTO and helps uncover issues early so they can be fixed before a real disaster.",
                "Emphasise that untested backups may be useless; restore testing validates both data and process.",
                "backup,disaster",
                "Many organisations discover backup problems only after an incident, when it's too late.",
            )
            sa(
                "Give an example of how poor change management can lead to data integrity issues.",
                "If a database administrator makes an unapproved change directly in production (for example, altering a table structure or running an update script without testing), it could corrupt data or break application logic. Without proper change requests, approvals, testing, and rollback plans, such changes may not be documented or easily reversible, leading to long‑lasting integrity problems.",
                "Look for a concrete scenario linking uncontrolled changes to corrupted or inconsistent data.",
                "integrity,change",
                "Good change management is a key control for preserving integrity.",
            )
            sa(
                "How can audit logs help detect and investigate a suspected data breach?",
                "Audit logs record who accessed which systems or records, when, and what actions they performed. In a suspected breach, investigators can use logs to see which accounts logged in, from where, what queries were run, what data was exported, and whether access patterns were unusual. This helps determine the scope of the breach, how it occurred, and which controls failed.",
                "Connect logs to detection (spotting anomalies) and investigation (reconstructing events and scope).",
                "audit,integrity",
                "Logs must be protected against tampering to be trustworthy.",
            )

        cur.executemany(
            """
            INSERT INTO short_answer_questions (unit_id, question, model_answer, explanation, tags, context)
            VALUES (?, ?, ?, ?, ?, ?);
        """,
            sa_qs,
        )

    # Persist SA seed version
    if sa_version_changed:
        cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", ("sa_seed_version", SA_SEED_VERSION))

    # ─── Seed explain-it-back topics ──────────────────────────────
    for ucode in ("ICTNWK421", "ICTNWK423"):
        u = cur.execute("SELECT id FROM units WHERE code = ?;", (ucode,)).fetchone()
        if not u:
            continue
        unit_id = int(u["id"])

        existing = cur.execute("SELECT COUNT(*) AS n FROM explain_topics WHERE unit_id = ?;", (unit_id,)).fetchone()[
            "n"
        ]
        if existing > 0:
            continue

        topics = []

        def topic(prompt, explanation, tags=""):
            topics.append((unit_id, prompt.strip(), explanation.strip(), tags))

        if ucode == "ICTNWK421":
            topic(
                "Explain how a stateful firewall works and why it is preferred over a stateless firewall in most enterprise networks.",
                "A stateful firewall tracks the state of connections (new, established, related) and automatically allows legitimate return traffic while blocking unexpected packets. This makes rule sets simpler and more secure than stateless firewalls, which evaluate each packet in isolation without context. Stateful inspection helps prevent many spoofing and scanning attacks by ensuring packets belong to valid sessions.",
                "firewall,stateful",
            )
            topic(
                "Describe defence in depth and give three specific examples of layers you would implement in a small business network.",
                "Defence in depth means using multiple independent security layers so that if one control fails, others still protect the system. For a small business this might include: a perimeter firewall controlling inbound/outbound traffic, endpoint protection (AV/EDR) on all workstations and servers, network segmentation with VLANs and ACLs to separate guests, staff, and servers, and strong access controls like MFA on remote access and admin accounts.",
                "principles,defence",
            )
            topic(
                "Explain why SSH is preferred over Telnet and how SSH key-based authentication improves security.",
                "Telnet sends all traffic, including usernames and passwords, in plaintext, which makes it easy for attackers to capture credentials on the network. SSH encrypts the entire session using strong cryptography so captured packets are not readable. SSH key-based authentication is even stronger because the private key never leaves the client device and is difficult to brute-force; the server only needs to verify possession of the matching private key.",
                "ssh,telnet,access",
            )
            topic(
                "Describe how 802.1X is used to secure access to a wired or wireless network.",
                "802.1X is a port-based access control protocol that requires devices to authenticate before gaining full network access. On Wi‑Fi it is typically used with WPA2/WPA3‑Enterprise and a RADIUS server: the access point acts as an authenticator, forwarding credentials to RADIUS, which validates the user or device. Until authentication succeeds, the port or SSID only allows restricted or guest access.",
                "wireless,access",
            )
            topic(
                "Explain what a rogue access point is and why it is dangerous.",
                "A rogue access point is an unauthorised wireless AP connected to the network or imitating it. Because it is outside normal security configuration and monitoring, it may provide weak or no encryption, allow unauthenticated access to the internal LAN, or be used by attackers for man‑in‑the‑middle attacks. It bypasses carefully designed perimeter and access controls.",
                "wireless,threats",
            )
        if ucode == "ICTNWK423":
            topic(
                "Explain the difference between RPO and RTO and how each affects backup and recovery design.",
                "RPO (Recovery Point Objective) is how much data loss, measured in time, the business can tolerate (e.g. 4 hours of data). It drives how frequently you must take backups or replicate data. RTO (Recovery Time Objective) is how long systems can be down before they must be restored (e.g. 2 hours). It influences the choice of recovery infrastructure, such as warm standbys, clustering, or slower tape restores.",
                "backup,disaster",
            )
            topic(
                "Describe why RAID alone is not enough to provide data protection and why backups are still required.",
                "RAID provides hardware redundancy by allowing an array to survive one or more disk failures without data loss, but it does not protect against accidental deletion, logical corruption, ransomware, or site-wide disasters. When data is deleted or encrypted by malware, RAID simply keeps multiple exact copies of the bad data. Separate backups taken at earlier points in time are required to restore clean versions.",
                "raid,backup",
            )
            topic(
                "Explain how audit logging helps maintain data integrity in an organisation.",
                "Audit logs record who did what, when, and on which systems or data. Knowing that actions are logged encourages responsible behaviour, and when something goes wrong the logs provide a trail to see which accounts accessed or modified data. This supports detecting unauthorised changes, investigating incidents, and demonstrating compliance with policies or regulations.",
                "audit,integrity",
            )
            topic(
                "Describe a simple four-level data classification scheme and how it influences handling of information.",
                "A simple scheme might be: Public, Internal, Confidential, and Highly Confidential. Public information can be shared freely; Internal is for staff only; Confidential is restricted to staff with a need-to-know and must be stored on company systems only; Highly Confidential (e.g. personal or financial data) requires encryption at rest, stricter access controls, and monitoring. Each level has specific storage, transmission, and access rules.",
                "classification,privacy",
            )
            topic(
                "Explain what a Business Continuity Plan (BCP) is and how it relates to Disaster Recovery.",
                "A Business Continuity Plan describes how critical business processes will continue during and after a disruption, using workarounds, alternate sites, or manual procedures. Disaster Recovery focuses on restoring IT systems and data. Together they ensure that the organisation can keep operating at an acceptable level while technical recovery is underway, and then return to normal service.",
                "business_continuity,disaster",
            )

        if topics:
            cur.executemany(
                """
                INSERT INTO explain_topics (unit_id, topic_prompt, model_explanation, tags)
                VALUES (?, ?, ?, ?);
            """,
                topics,
            )

    con.commit()
    con.close()
