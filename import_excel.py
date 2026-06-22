import openpyxl
import sqlite3
from datetime import datetime

# Read the Excel file
wb = openpyxl.load_workbook("dsa_revision_tracker.xlsx")
ws = wb["Log"]

# Connect to the database
conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()

count = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    problem = row[1]
    if not problem:
        continue

    pattern = row[2]
    difficulty = row[3]
    first_done = row[4]
    status = row[5]
    next_revisit = row[8]

    cursor.execute("""
        INSERT INTO problems (problem, pattern, difficulty, first_done, status, next_revisit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (problem, pattern, difficulty, first_done, status, next_revisit))

    count += 1

conn.commit()
conn.close()

print(f"Imported {count} problems.")