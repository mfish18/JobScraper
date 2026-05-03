import sqlite3
import os
import json
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/jobs.db")

#comprehensive skill taxonomy (gen'd by AI)
SKILL_TAXONOMY = {
    # ── Languages ──────────────────────────────────────────────
    "python", "sql", "scala", "java", "javascript", "typescript",
    "bash", "shell", "c++", "c#", "go", "rust", "julia", "matlab",
    "sas", "stata", "vba", "php", "swift", "kotlin", "perl",
    "python3", "python 3", "t-sql", "tsql", "pl/sql", "plsql",
    "c programming", "c/c++", "c / c++",
    "r programming", "r language",

    # ── ML / AI / Data Science ─────────────────────────────────
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "supervised learning",
    "unsupervised learning", "transfer learning", "feature engineering",
    "feature selection", "model evaluation", "model deployment",
    "hypothesis testing", "a/b testing", "statistical modeling",
    "time series", "forecasting", "anomaly detection", "recommendation systems",
    "classification", "regression", "clustering", "dimensionality reduction",
    "neural networks", "convolutional neural networks", "recurrent neural networks",
    "transformers", "attention mechanism", "llm", "large language models",
    "generative ai", "diffusion models", "gans", "rag",
    "retrieval augmented generation", "prompt engineering", "fine-tuning",
    "embeddings", "vector search", "semantic search",

    # ── ML Frameworks & Libraries ──────────────────────────────
    "pytorch", "tensorflow", "keras", "scikit-learn", "xgboost",
    "lightgbm", "catboost", "hugging face", "langchain", "llamaindex",
    "spacy", "nltk", "gensim", "opencv", "onnx", "triton", "ray", "dask",

    # ── Data Engineering & Processing ──────────────────────────
    "pandas", "numpy", "polars", "spark", "pyspark", "hadoop",
    "kafka", "flink", "airflow", "prefect", "dagster", "luigi",
    "dbt", "fivetran", "stitch", "airbyte", "databricks",
    "data pipelines", "etl", "elt", "data warehousing", "data lake",
    "data lakehouse", "data modeling", "data quality", "data governance",
    "data lineage", "data catalog", "data mesh",

    # ── Databases ──────────────────────────────────────────────
    "postgresql", "mysql", "sqlite", "oracle", "sql server", "mssql",
    "mongodb", "cassandra", "redis", "elasticsearch", "opensearch",
    "neo4j", "dynamodb", "firestore", "couchdb", "influxdb",
    "bigquery", "redshift", "snowflake", "duckdb", "clickhouse",
    "pinecone", "weaviate", "chroma", "qdrant", "pgvector",
    "google bigquery", "amazon redshift",

    # ── Cloud Platforms ────────────────────────────────────────
    "aws", "azure", "gcp", "google cloud", "ibm cloud", "oracle cloud",
    "s3", "ec2", "lambda", "rds", "emr", "glue", "athena",
    "sagemaker", "bedrock", "azure ml", "vertex ai", "azure databricks",
    "cloud functions", "cloud run", "azure synapse",
    "azure data factory", "azure blob storage",
    "amazon sagemaker", "amazon ec2", "amazon s3", "amazon rds",

    # ── MLOps & DevOps ─────────────────────────────────────────
    "mlflow", "kubeflow", "metaflow", "bentoml", "seldon", "torchserve",
    "docker", "kubernetes", "helm", "terraform", "ansible",
    "ci/cd", "github actions", "jenkins", "gitlab ci", "circleci",
    "git", "github", "gitlab", "bitbucket",
    "prometheus", "grafana", "datadog", "new relic", "splunk",

    # ── Data Visualization & BI ────────────────────────────────
    "tableau", "power bi", "looker", "looker studio", "qlik",
    "metabase", "superset", "redash", "mode", "sigma",
    "matplotlib", "seaborn", "plotly", "bokeh", "altair",
    "streamlit", "dash", "gradio", "d3.js",
    "power automate", "power apps", "power platform",

    # ── Web & API Development ──────────────────────────────────
    "fastapi", "flask", "django", "rest api", "graphql", "grpc",
    "react", "node.js", "express", "html", "css",
    "postman", "swagger", "openapi",

    # ── Statistics & Mathematics ───────────────────────────────
    "statistics", "probability", "linear algebra", "calculus",
    "bayesian inference", "bayesian statistics", "causal inference",
    "experimental design", "regression analysis", "multivariate analysis",
    "monte carlo", "optimization", "operations research",

    # ── Analytics & Business Intelligence ─────────────────────
    "business intelligence", "data analysis", "exploratory data analysis",
    "eda", "kpi", "metrics", "dashboards", "reporting",
    "excel", "google sheets", "pivot tables", "vlookup",
    "ms excel", "microsoft excel", "advanced excel",
    "google analytics", "mixpanel", "amplitude", "segment",
    "product analytics", "marketing analytics", "financial modeling",

    # ── Soft Skills & Methodology ──────────────────────────────
    "agile", "scrum", "kanban", "jira", "confluence",
    "communication", "stakeholder management", "project management",
    "problem solving", "critical thinking", "teamwork", "collaboration",
    "presentation skills", "data storytelling", "technical writing",
    "mentoring", "leadership", "cross-functional",

    # ── Domain Knowledge ───────────────────────────────────────
    "finance", "healthcare", "retail", "e-commerce", "supply chain",
    "logistics", "manufacturing", "telecommunications", "cybersecurity",
    "fraud detection", "risk management", "compliance",
    "digital marketing", "seo", "crm", "salesforce",

    # ── Other Tools ────────────────────────────────────────────
    "linux", "unix", "jupyter", "vs code", "pycharm", "rstudio",
    "databricks notebooks", "google colab", "notion", "confluence",
    "microsoft teams", "sharepoint",
}

# Single-letter or very short skills — must not match inside longer words
STRICT_MATCH_SKILLS = {
    "go", "sas",
}

# Multi-word phrases — substring match is sufficient
PHRASE_SKILLS = {
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "reinforcement learning", "time series",
    "data pipelines", "data warehousing", "data lake", "data modeling",
    "data quality", "data governance", "large language models",
    "generative ai", "prompt engineering", "retrieval augmented generation",
    "sql server", "google cloud", "azure data factory", "azure synapse",
    "azure blob storage", "azure databricks", "azure ml",
    "rest api", "ci/cd", "a/b testing", "feature engineering",
    "neural networks", "recommendation systems", "anomaly detection",
    "business intelligence", "exploratory data analysis",
    "stakeholder management", "cross-functional", "data storytelling",
    "financial modeling", "fraud detection", "risk management",
    "power bi", "looker studio", "power automate", "power apps",
    "power platform", "google analytics", "google sheets",
    "google bigquery", "amazon redshift", "amazon sagemaker",
    "amazon ec2", "amazon s3", "amazon rds", "github actions",
    "gitlab ci", "node.js", "scikit-learn", "hugging face",
    "ms excel", "microsoft excel", "advanced excel",
    "pivot tables", "product analytics", "marketing analytics",
    "presentation skills", "technical writing", "project management",
    "problem solving", "critical thinking", "data analysis",
    "model evaluation", "model deployment", "transfer learning",
    "supervised learning", "unsupervised learning", "causal inference",
    "experimental design", "regression analysis", "multivariate analysis",
    "supply chain", "digital marketing", "e-commerce",
    "c programming", "c/c++", "c / c++",
    "r programming", "r language",
}

#takes text and grabs the skills from it based on taxonomy
def extract_skills_from_text(text: str) -> list:
    if not text:
        return []

    text_lower = text.lower()
    found = set()

    for skill in SKILL_TAXONOMY:
        #if the skill is a strict match(short strings that could be taken out of other words ie 'c')
        if skill in STRICT_MATCH_SKILLS:
            pattern = r'(?<![a-zA-Z])' + re.escape(skill) + r'(?![a-zA-Z])'
            if re.search(pattern, text_lower):
                found.add(skill)
        #matching substrings that could appear in various manners
        elif skill in PHRASE_SKILLS:
            if skill in text_lower:
                found.add(skill)
        #whole word matching from taxonomy
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)

    return sorted(list(found))

def process_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #add skills column if it doesn't exist yet
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN skills TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    #reset all so they get re-extracted with updated taxonomy (dev work)
    cursor.execute("UPDATE jobs SET skills = NULL")
    conn.commit()

    #get all of the unprocessed jobs to process
    cursor.execute("SELECT id, description FROM jobs WHERE skills IS NULL")
    jobs = cursor.fetchall()

    print(f"Processing {len(jobs)} jobs...")

    for job_id, description in jobs:
        skills = extract_skills_from_text(description)
        skills_json = json.dumps(skills)
        cursor.execute(
            "UPDATE jobs SET skills = ? WHERE id = ?",
            (skills_json, job_id)
        )

    conn.commit()
    conn.close()
    print("Done. Skills extracted and saved.")

#gets the occurrences of each of the skills to get frequency
def get_skill_frequency():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT skills FROM jobs WHERE skills IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    frequency = {}
    for (skills_json,) in rows:
        skills = json.loads(skills_json)
        for skill in skills:
            frequency[skill] = frequency.get(skill, 0) + 1

    return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))

if __name__ == "__main__":
    process_all_jobs()

    print("\nTop 20 most in-demand skills across all jobs found:")
    freq = get_skill_frequency()
    for skill, count in list(freq.items())[:20]:
        print(f"{skill:<30} {count:>3}")