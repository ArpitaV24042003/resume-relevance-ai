import sqlite3
import os

# Use an absolute path to ensure the DB is created in the correct location
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'results.db')

# Initialize DB tables
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # We don't need separate tables for resumes and JDs for this version
    # This simplifies the logic significantly.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_filename TEXT,
        jd_filename TEXT,
        hard_score REAL,
        semantic_score REAL,
        weighted_score REAL,
        verdict TEXT,
        matched_skills TEXT,
        missing_skills TEXT,
        suggestions TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Save a complete evaluation record
def save_evaluation(
    resume_filename, jd_filename, hard_score, semantic_score,
    weighted_score, verdict, matched_skills, missing_skills, suggestions
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    INSERT INTO evaluations
    (resume_filename, jd_filename, hard_score, semantic_score, weighted_score, verdict, matched_skills, missing_skills, suggestions)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_filename, jd_filename, hard_score, semantic_score,
        weighted_score, verdict, ",".join(matched_skills),
        ",".join(missing_skills), ";".join(suggestions) # Using semicolon for suggestions
    ))
    conn.commit()
    conn.close()

# Fetch all evaluation records for the dashboard
def get_evaluations():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Adding a reasonable LIMIT to prevent fetching too much data
    c.execute("SELECT id, resume_filename, jd_filename, hard_score, semantic_score, weighted_score, verdict, matched_skills, missing_skills, suggestions FROM evaluations ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return rows
