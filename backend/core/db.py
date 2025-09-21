# backend/db.py
import sqlite3

conn = sqlite3.connect("results.db", check_same_thread=False)
c = conn.cursor()

# Tables
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

def save_resume(data):
    c.execute('''
    INSERT INTO resumes (filename, student_name, email, phone, skills, raw_text)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.get("filename"), data.get("student_name"), data.get("email"),
          data.get("phone"), ",".join(data.get("skills", [])), data.get("raw_text")))
    conn.commit()
    return c.lastrowid

def save_job_description(data):
    c.execute('''
    INSERT INTO job_descriptions (filename, role_title, must_have_skills, good_to_have_skills, qualifications, raw_text)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.get("filename"), data.get("role_title"),
          ",".join(data.get("must_have_skills", [])),
          ",".join(data.get("good_to_have_skills", [])),
          data.get("qualifications"), data.get("raw_text")))
    conn.commit()
    return c.lastrowid
