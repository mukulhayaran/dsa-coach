import sqlite3

conn = sqlite3.connect("dsa_coach.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem TEXT NOT NULL,
        pattern TEXT,
        difficulty TEXT,
        first_done DATE,
        status TEXT DEFAULT 'SEEDED',
        next_revisit DATE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id INTEGER NOT NULL,
        attempt_date DATE,
        result TEXT,
        confidence INTEGER,
        time_taken_minutes INTEGER,
        note TEXT,
        FOREIGN KEY (problem_id) REFERENCES problems(id)
    )
""")

conn.commit()
conn.close()

print("Database created successfully.")