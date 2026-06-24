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


st.subheader("All Problems")

conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        p.problem, p.pattern, p.difficulty, p.status, p.next_revisit,
        a.attempt_date, a.result, a.note
    FROM problems p
    LEFT JOIN attempts a ON a.id = (
        SELECT id FROM attempts WHERE problem_id = p.id ORDER BY attempt_date DESC LIMIT 1
    )
    ORDER BY p.pattern, p.problem
""")
all_problems = cursor.fetchall()
conn.close()

for row in all_problems:
    problem, pattern, difficulty, status, next_revisit, last_attempt, result, note = row
    st.write(f"**{problem}** ({pattern}, {difficulty}) — Status: {status} — Next: {next_revisit}")
    if last_attempt:
        st.caption(f"Last attempt: {last_attempt} — {result} — {note or ''}")