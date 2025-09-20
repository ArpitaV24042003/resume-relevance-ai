import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("results.db", check_same_thread=False)
c = conn.cursor()

# -----------------------------
# TABLE CREATION
# -----------------------------
c.execute('''
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    student_name TEXT,
    email TEXT,
    phone TEXT,
    skills TEXT,
    raw_text TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    role_title TEXT,
    must_have_skills TEXT,
    good_to_have_skills TEXT,
    qualifications TEXT,
    raw_text TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER,
    jd_id INTEGER,
    hard_score REAL,
    semantic_score REAL,
    weighted_score REAL,
    verdict TEXT,
    matched_skills TEXT,
    missing_skills TEXT,
    suggestions TEXT,
    FOREIGN KEY(resume_id) REFERENCES resumes(id),
    FOREIGN KEY(jd_id) REFERENCES job_descriptions(id)
)
''')

conn.commit()

# -----------------------------
# INSERT FUNCTIONS
# -----------------------------
def save_resume(data):
    c.execute('''
    INSERT INTO resumes (filename, student_name, email, phone, skills, raw_text)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get("filename"),
        data.get("student_name"),
        data.get("email"),
        data.get("phone"),
        ",".join(data.get("skills", [])),
        data.get("raw_text")
    ))
    conn.commit()
    return c.lastrowid  # return new resume ID

def save_job_description(data):
    c.execute('''
    INSERT INTO job_descriptions (filename, role_title, must_have_skills, good_to_have_skills, qualifications, raw_text)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get("filename"),
        data.get("role_title"),
        ",".join(data.get("must_have_skills", [])),
        ",".join(data.get("good_to_have_skills", [])),
        data.get("qualifications"),
        data.get("raw_text")
    ))
    conn.commit()
    return c.lastrowid  # return new JD ID

def save_evaluation(data):
    c.execute('''
    INSERT INTO evaluations (resume_id, jd_id, hard_score, semantic_score, weighted_score, verdict, matched_skills, missing_skills, suggestions)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("resume_id"),
        data.get("jd_id"),
        data.get("hard_score"),
        data.get("semantic_score"),
        data.get("weighted_score"),
        data.get("verdict"),
        ",".join(data.get("matched_skills", [])),
        ",".join(data.get("missing_skills", [])),
        ",".join(data.get("suggestions", []))
    ))
    conn.commit()
    return c.lastrowid

# -----------------------------
# FETCH FUNCTIONS
# -----------------------------
def get_resumes():
    c.execute("SELECT * FROM resumes")
    return c.fetchall()

def get_job_descriptions():
    c.execute("SELECT * FROM job_descriptions")
    return c.fetchall()

def get_evaluations():
    c.execute('''
    SELECT e.id, r.filename, j.filename, e.hard_score, e.semantic_score, e.weighted_score, e.verdict, e.matched_skills, e.missing_skills, e.suggestions
    FROM evaluations e
    JOIN resumes r ON e.resume_id = r.id
    JOIN job_descriptions j ON e.jd_id = j.id
    ''')
    return c.fetchall()
