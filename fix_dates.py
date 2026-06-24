import sqlite3
from datetime import date, timedelta

today = date(2026, 6, 24)
MAX_PER_DAY = 5

conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()

status_priority = {"SEEDED": 0, "COLD-1": 1, "COLD-2": 2, "OWNED": 3}

# Get every overdue problem (excluding OWNED, since those are on a long recheck cycle)
cursor.execute("""
    SELECT id, status, next_revisit FROM problems
    WHERE next_revisit <= ? AND status != 'OWNED'
""", (today.isoformat(),))

rows = cursor.fetchall()

# Sort by urgency: status severity first, then oldest next_revisit first
rows.sort(key=lambda r: (status_priority.get(r[1], 1), r[2] or ""))

print(f"Found {len(rows)} overdue problems (excluding OWNED).")

for i, (problem_id, status, old_revisit) in enumerate(rows):
    day_offset = i // MAX_PER_DAY
    new_date = today + timedelta(days=day_offset)
    cursor.execute(
        "UPDATE problems SET next_revisit = ? WHERE id = ?",
        (new_date.isoformat(), problem_id)
    )
    print(f"id={problem_id} status={status} {old_revisit} -> {new_date}")

conn.commit()
conn.close()
print("Done.")