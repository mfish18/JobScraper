import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def create_tables():
    #Supabase requires tables to be created in the dashboard or via migrations
    #no-op here but kept so the pipeline call doesn't break
    print("Tables managed via Supabase dashboard.")

def save_jobs(jobs: list):
    supabase = get_client()
    saved = 0
    skipped = 0

    for job in jobs:
        job_id = job.get("id")
        try:
            row = {
                "id": job_id,
                "title": job.get("title"),
                "company": job.get("company", {}).get("display_name"),
                "location": job.get("location", {}).get("display_name"),
                "description": job.get("description"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "date_posted": job.get("created"),
                "date_collected": datetime.utcnow().isoformat(),
                "redirect_url": job.get("redirect_url"),
            }

            result = supabase.table("jobs").upsert(row, on_conflict="id", ignore_duplicates=True).execute()

            if result.data:
                saved += 1
            else:
                skipped += 1

        except Exception as e:
            print(f"Error saving job {job_id}: {e}")

    print(f"Saved: {saved} new jobs | Skipped: {skipped} duplicates")
    return saved, skipped

def get_all_jobs():
    supabase = get_client()
    result = supabase.table("jobs").select("*").execute()
    return result.data