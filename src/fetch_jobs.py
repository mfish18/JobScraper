import requests
import json
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
    for keyword in searches:
        print(f"\nFetching: {keyword}")
        data = fetch_jobs(keywords=keyword, results_per_page=50)
        save_jobs(data["results"])
    
    print(f"Total jobs found: {data['count']}")
    save_jobs(data["results"])     
    
    for job in data["results"][:3]:
        print(f"Title:    {job['title']}")
        print(f"Company:  {job.get('company', {}).get('display_name', 'N/A')}")
        print(f"Location: {job.get('location', {}).get('display_name', 'N/A')}")
        print(f"Salary:   {job.get('salary_min', 'N/A')} - {job.get('salary_max', 'N/A')}")
        print(f"Posted:   {job.get('created', 'N/A')}")
        print()