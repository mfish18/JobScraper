import os
import json
import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="📊",
    layout="wide"
)

#load data from db

@st.cache_data
def load_jobs():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()
    return df

@st.cache_data
def get_skill_frequency(df, role_filter=None):
    if role_filter and role_filter != "All":
        df = df[df["title"].str.contains(role_filter, case=False, na=False)]

    frequency = {}
    for skills_val in df["skills"].dropna():
        #handle both string (sqlite) and list (postgresql) formats
        if isinstance(skills_val, str):
            skills = json.loads(skills_val)
        else:
            skills = skills_val

        for skill in skills:
            frequency[skill] = frequency.get(skill, 0) + 1

    return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))

df = load_jobs()
df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
df["date_collected"] = pd.to_datetime(df["date_collected"], errors="coerce")

#side bar filters

st.sidebar.title("Filters")

role_options = ["All", "Data Analyst", "Data Scientist", "Machine Learning",
                "Data Engineer", "Software Engineer", "QA"]
selected_role = st.sidebar.selectbox("Role type", role_options)

top_n = st.sidebar.slider("Show top N skills", min_value=5, max_value=50, value=20)

st.title("📊 Job Market Intelligence Engine")
st.caption("Canadian job market - data, ML, and engineering roles")

#key performance indicators

col1, col2, col3, col4 = st.columns(4)

filtered_df = df if selected_role == "All" else df[
    df["title"].str.contains(selected_role, case=False, na=False)
]

with col1:
    st.metric("Total jobs collected", len(df))
with col2:
    st.metric("Filtered jobs", len(filtered_df))
with col3:
    has_salary = filtered_df["salary_min"].notna().sum()
    st.metric("Jobs with salary data", has_salary)
with col4:
    if has_salary > 0:
        avg_salary = filtered_df["salary_min"].dropna().mean()
        st.metric("Avg salary (min)", f"${avg_salary:,.0f}")
    else:
        st.metric("Avg salary (min)", "N/A")

st.divider()

#msot frequent skills chart

st.subheader(f"Top {top_n} most in-demand skills — {selected_role}")

freq = get_skill_frequency(filtered_df, selected_role)
top_skills = dict(list(freq.items())[:top_n])

if top_skills:
    skill_df = pd.DataFrame({
        "skill": list(top_skills.keys()),
        "count": list(top_skills.values())
    })

    fig = px.bar(
        skill_df,
        x="count",
        y="skill",
        orientation="h",
        color="count",
        color_continuous_scale="teal",
        labels={"count": "Job postings", "skill": ""},
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=600,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

#salary distribution

st.subheader("Salary distribution")

salary_df = filtered_df.dropna(subset=["salary_min", "salary_max"])
salary_df = salary_df[(salary_df["salary_min"] > 1000)]

if len(salary_df) > 0:
    fig2 = px.histogram(
        salary_df,
        x="salary_min",
        nbins=20,
        labels={"salary_min": "Salary (min posted)", "count": "Jobs"},
        color_discrete_sequence=["#2a9d8f"]
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Not enough salary data for this filter. Most Canadian postings don't include salary — this will improve as you collect more data.")

st.divider()

#most active companies (based on postings)

st.subheader("Most active hiring companies")

company_counts = (
    filtered_df["company"]
    .dropna()
    .value_counts()
    .head(15)
    .reset_index()
)
company_counts.columns = ["company", "postings"]

fig3 = px.bar(
    company_counts,
    x="postings",
    y="company",
    orientation="h",
    color="postings",
    color_continuous_scale="purples",
    labels={"postings": "Job postings", "company": ""},
)
fig3.update_layout(
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
    height=450,
    margin=dict(l=0, r=0, t=20, b=0),
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

#raw data table

st.subheader("Raw job data")

show_cols = ["title", "company", "location", "salary_min", "salary_max", "date_posted"]
st.dataframe(
    filtered_df[show_cols].sort_values("date_posted", ascending=False),
    use_container_width=True,
    hide_index=True
)