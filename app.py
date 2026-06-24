import streamlit as st
import sqlite3

from scheduler import calculate_next_status
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


st.subheader("Log an Attempt")

conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()
cursor.execute("SELECT id, problem, status FROM problems ORDER BY problem")
all_for_dropdown = cursor.fetchall()
conn.close()

problem_options = {f"{p[1]} ({p[2]})": p for p in all_for_dropdown}
selected_label = st.selectbox("Which problem?", list(problem_options.keys()))
result = st.radio("Result", ["Cold", "Help"])
note = st.text_input("Note (optional)")

if st.button("Submit"):
    problem_id, problem_name, current_status = problem_options[selected_label]
    today = date.today()

    new_status, next_revisit = calculate_next_status(current_status, result, today)

    conn = sqlite3.connect("dsa_coach.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO attempts (problem_id, attempt_date, result, note) VALUES (?, ?, ?, ?)",
        (problem_id, today.isoformat(), result, note)
    )

    cursor.execute(
        "UPDATE problems SET status = ?, next_revisit = ? WHERE id = ?",
        (new_status, next_revisit.isoformat() if next_revisit else None, problem_id)
    )

    conn.commit()
    conn.close()

    st.success(f"Logged. {problem_name} moved to {new_status}, next revisit: {next_revisit}")


st.subheader("Weak Patterns")

conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT p.pattern, 
           SUM(CASE WHEN a.result = 'Help' THEN 1 ELSE 0 END) AS help_count,
           COUNT(a.id) AS total_attempts
    FROM problems p
    JOIN attempts a ON a.problem_id = p.id
    GROUP BY p.pattern
    ORDER BY help_count DESC
""")
pattern_stats = cursor.fetchall()
conn.close()

for pattern, help_count, total in pattern_stats:
    st.write(f"**{pattern}** — {help_count} Help / {total} total attempts")