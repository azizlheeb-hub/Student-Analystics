import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

DB_PATH = Path(__file__).with_name("student_performance.db")

st.set_page_config(page_title="Student Performance Analytics", page_icon="📊", layout="wide")

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL,
                course_name TEXT NOT NULL,
                credits INTEGER NOT NULL CHECK (credits > 0),
                grade_points REAL NOT NULL CHECK (grade_points >= 0 AND grade_points <= 4),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

def load_data():
    with connect() as conn:
        return pd.read_sql_query(
            "SELECT id, term, course_name, credits, grade_points FROM courses ORDER BY term, course_name",
            conn
        )

def weighted_gpa(df):
    if df.empty or df["credits"].sum() == 0:
        return 0.0
    return float((df["credits"] * df["grade_points"]).sum() / df["credits"].sum())

init_db()
st.title("📊 Student Performance Analytics")
st.caption("Track courses, calculate weighted GPA, and explore academic progress.")

with st.sidebar:
    st.header("Add a course")
    with st.form("add_course", clear_on_submit=True):
        term = st.text_input("Term / semester", placeholder="e.g. Fall 2026")
        course_name = st.text_input("Course name", placeholder="e.g. Data Structures")
        credits = st.number_input("Credit hours", min_value=1, max_value=30, value=3, step=1)
        grade = st.number_input("Grade points (0.00–4.00)", min_value=0.0, max_value=4.0, value=3.0, step=0.25)
        submitted = st.form_submit_button("Save course", use_container_width=True)
        if submitted:
            if not term.strip() or not course_name.strip():
                st.error("Enter both a term and a course name.")
            else:
                with connect() as conn:
                    conn.execute(
                        "INSERT INTO courses (term, course_name, credits, grade_points) VALUES (?, ?, ?, ?)",
                        (term.strip(), course_name.strip(), int(credits), float(grade))
                    )
                st.success("Course saved.")
                st.rerun()

df = load_data()
if df.empty:
    st.info("Add your first course from the sidebar to begin.")
else:
    total_credits = int(df["credits"].sum())
    overall_gpa = weighted_gpa(df)
    terms = sorted(df["term"].unique())
    term_gpas = df.groupby("term").apply(weighted_gpa, include_groups=False).reset_index(name="GPA")

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall GPA", f"{overall_gpa:.2f} / 4.00")
    c2.metric("Completed credit hours", total_credits)
    c3.metric("Courses tracked", len(df))

    st.subheader("Semester performance")
    if not term_gpas.empty:
        fig = px.bar(term_gpas, x="term", y="GPA", text_auto=".2f",
                     title="Weighted GPA by term", range_y=[0, 4])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Course records")
    edited = st.data_editor(
        df[["id", "term", "course_name", "credits", "grade_points"]],
        hide_index=True, use_container_width=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "term": st.column_config.TextColumn("Term"),
            "course_name": st.column_config.TextColumn("Course"),
            "credits": st.column_config.NumberColumn("Credits", min_value=1, step=1),
            "grade_points": st.column_config.NumberColumn("Grade points", min_value=0.0, max_value=4.0, step=0.25),
        },
        disabled=["id"]
    )
    if st.button("Save table edits"):
        with connect() as conn:
            for _, row in edited.iterrows():
                conn.execute(
                    "UPDATE courses SET term=?, course_name=?, credits=?, grade_points=? WHERE id=?",
                    (str(row["term"]).strip(), str(row["course_name"]).strip(),
                     int(row["credits"]), float(row["grade_points"]), int(row["id"]))
                )
        st.success("Changes saved.")
        st.rerun()

    left, right = st.columns([1, 2])
    with left:
        st.subheader("Delete a course")
        selected = st.selectbox(
            "Choose record",
            df["id"].tolist(),
            format_func=lambda x: f"#{x} — {df.loc[df.id == x, 'course_name'].iloc[0]}"
        )
        if st.button("Delete selected course", type="secondary"):
            with connect() as conn:
                conn.execute("DELETE FROM courses WHERE id=?", (int(selected),))
            st.rerun()
    with right:
        st.subheader("Export")
        st.download_button(
            "Download CSV",
            data=df.drop(columns=["id"]).to_csv(index=False).encode("utf-8"),
            file_name="academic_records.csv",
            mime="text/csv"
        )

    st.subheader("Grade distribution")
    fig2 = px.histogram(df, x="grade_points", nbins=8, range_x=[0, 4],
                        labels={"grade_points": "Grade points", "count": "Courses"})
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("Built with Python, Streamlit, SQLite, Pandas, and Plotly.")
