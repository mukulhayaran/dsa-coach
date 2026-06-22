import openpyxl
import sqlite3

wb = openpyxl.load_workbook("dsa_revision_tracker.xlsx")
ws = wb["Log"]

conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()

count = 0
problem_index = 1  # tracks which problem this row corresponds to, in import order

for row in ws.iter_rows(min_row=2, values_only=True):
    problem_name = row[1]
    if not problem_name:
        continue

    last_attempt = row[6]
    result = row[7]
    note = row[9]

    if last_attempt is None and result is None and note is None:
        problem_index += 1
        continue  # nothing to import for this problem

    cursor.execute("""
        INSERT INTO attempts (problem_id, attempt_date, result, note)
        VALUES (?, ?, ?, ?)
    """, (problem_index, last_attempt, result, note))

    count += 1
    problem_index += 1

conn.commit()
conn.close()

print(f"Imported {count} attempt records.")