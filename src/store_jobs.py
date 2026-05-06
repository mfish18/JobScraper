import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id              TEXT PRIMARY KEY,
            title           TEXT,
            company         TEXT,
            location        TEXT,
            description     TEXT,
            salary_min      REAL,
            salary_max      REAL,
            date_posted     TEXT,
            date_collected  TEXT,
            redirect_url    TEXT,
            skills          TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created successfully.")

def save_jobs(jobs: list):
    conn = get_connection()
    cursor = conn.cursor()

    saved = 0
    skipped = 0

    for job in jobs:
        job_id = job.get("id")

        try:
            cursor.execute("""
                INSERT INTO jobs (
                    id, title, company, location, description,
                    salary_min, salary_max, date_posted, date_collected, redirect_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                job_id,
                job.get("title"),
                job.get("company", {}).get("display_name"),
                job.get("location", {}).get("display_name"),
                job.get("description"),
                job.get("salary_min"),
                job.get("salary_max"),
                job.get("created"),
                datetime.utcnow().isoformat(),
                job.get("redirect_url")
            ))

            if cursor.rowcount == 1:
                saved += 1
            else:
                skipped += 1

        except Exception as e:
            print(f"Error saving job {job_id}: {e}")
            conn.rollback()

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved: {saved} new jobs | Skipped: {skipped} duplicates")
    return saved, skipped

def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows