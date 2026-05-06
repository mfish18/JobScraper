import sys
import os
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from fetch_jobs import fetch_jobs
from store_jobs import save_jobs, create_tables
from fetch_skills import process_all_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler/pipeline.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

SEARCH_QUERIES = [
    "data analyst",
    "machine learning engineer",
    "data scientist",
    "ml engineer",
    "data engineer",
    "software engineer",
    "software developer",
    "qa analyst",
    "qa automation",
]

def run_pipeline():
    log.info("=" * 50)
    log.info(f"Pipeline started at {datetime.utcnow().isoformat()}")

    create_tables()

    total_saved = 0
    total_skipped = 0

    for query in SEARCH_QUERIES:
        log.info(f"Fetching: {query}")
        try:
            data = fetch_jobs(keywords=query, results_per_page=50)
            results = data.get("results", [])
            saved, skipped = save_jobs(results)
            total_saved += saved
            total_skipped += skipped
            log.info(f"  '{query}' -> saved {saved}, skipped {skipped}")

        except Exception as e:
            log.error(f"  Failed on '{query}': {e}")

    log.info(f"Fetch complete — total saved: {total_saved}, skipped: {total_skipped}")

    log.info("Running skill extraction...")
    process_all_jobs()

    log.info("Pipeline complete.")
    log.info("=" * 50)

if __name__ == "__main__":
    log.info("Scheduler starting up...")

    run_pipeline()

    scheduler = BlockingScheduler()

    scheduler.add_job(
        run_pipeline,
        CronTrigger(hour="9,18", minute="0"),
        id="job_pipeline",
        name="Job market pipeline",
        misfire_grace_time=300
    )

    log.info("Scheduler running. Pipeline fires at 9am and 6pm daily.")
    log.info("Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Scheduler stopped.")