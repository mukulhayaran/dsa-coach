import streamlit as st
import sqlite3
from datetime import date

st.title("DSA Coach")

conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()

today = date.today().isoformat()

# Today's session - capped at 5, sorted by urgency
cursor.execute("""
    SELECT id, problem, pattern, status, next_revisit FROM problems
    WHERE next_revisit <= ? AND status != 'OWNED'
    ORDER BY 
        CASE status 
            WHEN 'SEEDED' THEN 0 
            WHEN 'COLD-1' THEN 1 
            WHEN 'COLD-2' THEN 2 
        END,
        next_revisit ASC
    LIMIT 5
""", (today,))
session_problems = cursor.fetchall()

# Total backlog count - honest number
cursor.execute("""
    SELECT COUNT(*) FROM problems
    WHERE next_revisit <= ? AND status != 'OWNED'
""", (today,))
total_backlog = cursor.fetchone()[0]

conn.close()

st.subheader("Today's Session")
for p in session_problems:
    st.write(f"**{p[1]}** — {p[2]} — Status: {p[3]} — Due: {p[4]}")

st.caption(f"Total backlog still waiting: {total_backlog}")