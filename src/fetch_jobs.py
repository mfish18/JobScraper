import requests
import os
from dotenv import load_dotenv
from store_jobs import save_jobs, create_tables

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

def fetch_jobs(keywords="software engineer", location="canada", results_per_page=10, page=1):
    url = f"https://api.adzuna.com/v1/api/jobs/ca/search/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": keywords,
        "where": location,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    create_tables()

    searches = [
        "data analyst",
        "machine learning engineer",
        "data scientist",
        "ML engineer",
        "data engineer",
        "software engineer",
        "software developer",
        "qa analyst",
        "qa automation"
    ]

    total_saved = 0
    total_skipped = 0

    for keyword in searches:
        print(f"\nFetching: {keyword}")
        data = fetch_jobs(keywords=keyword, results_per_page=50)
        results = data.get("results", [])
        saved, skipped = save_jobs(results)
        total_saved += saved
        total_skipped += skipped

    print(f"\nDone — total saved: {total_saved}, skipped: {total_skipped}")