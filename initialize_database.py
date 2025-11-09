import sqlite3

# Connect to database (creates file if it doesn't exist)
conn = sqlite3.connect("student_data.db")
cursor = conn.cursor()

# Create table for students
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_number TEXT UNIQUE NOT NULL,
    class TEXT,
    subject1 INTEGER,
    subject2 INTEGER,
    subject3 INTEGER,
    subject4 INTEGER,
    subject5 INTEGER
)
""")

conn.commit()
conn.close()

print("✅ Database 'student_data.db' created successfully with table 'students'.")
