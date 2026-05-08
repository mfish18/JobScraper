# Job Market Intelligence Engine

An automated pipeline that collects, processes, and visualizes Canadian job market data for data, ML, and engineering roles. Built to surface real skill demand trends and help identify gaps between a candidate's profile and the current market.

## What it does

- Pulls job postings twice daily from the Adzuna API across 9 role categories (to be expanded)
- Extracts in-demand skills from job descriptions using a custom NLP taxonomy
- Stores all data in a cloud PostgreSQL database (Supabase) for trend analysis
- Visualizes skill frequency, salary distribution, and hiring activity in an interactive Streamlit dashboard

## Tech stack

| Layer | Tools |
|---|---|
| Data collection | Python, Adzuna API, `requests` |
| NLP / skill extraction | `spaCy`, custom regex taxonomy |
| Storage | PostgreSQL (Supabase) |
| Orchestration | GitHub Actions (cron, twice daily) |
| Dashboard | Streamlit, Plotly |
| Environment | `python-dotenv`, `psycopg2` |

## Running locally

**1. Clone the repo**
```bash
git clone https://github.com/mfish18/JobScraper.git
cd JobScraper
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  #windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Set up environment variables**

Create a `.env` file in the project root:
```
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
DATABASE_URL=postgresql://postgres:[password]@db.xxxx.supabase.co:6543/postgres?sslmode=require
```

Get your Adzuna credentials at [developer.adzuna.com](https://developer.adzuna.com). Supabase connection string is under Project Settings → Database → Session pooler.

**4. Run the pipeline manually**
```bash
python scheduler/run_pipeline.py
```

**5. Launch the dashboard**
```bash
streamlit run dashboard/app.py
```

## Automated pipeline

The pipeline runs automatically via GitHub Actions at 9am and 6pm EST daily. It requires three repository secrets:

- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `SUPABASE_SERVICE_KEY`
- `SUPABASE_URL`

Set these under your repo → Settings → Secrets and variables → Actions.

## Key findings so far

- **Machine learning** is the most demanded skill across all role types, appearing in ~13% of all postings
- **Azure** dominates over AWS in the Canadian market, reflecting enterprise adoption in banking and telecom
- Salary data is sparse (~15% of postings) - a known gap in Canadian job board data
- QA automation roles are significantly more likely to post salary ranges than data/ML roles