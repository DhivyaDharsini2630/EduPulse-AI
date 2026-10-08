import os
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_NAME = os.path.join(PROJECT_ROOT, "users.db")


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            student_id TEXT
        )
    """)

    csv_path = os.path.join(
        PROJECT_ROOT, "data", "processed", "student_360.csv"
    )
    students = pd.read_csv(csv_path)
    student_password_hash = generate_password_hash("student123")

    users = []
    for _, student in students.iterrows():
        student_id = str(student["student_id"])
        number = student_id.replace("STU", "")
        users.append(("student" + number, student_password_hash, "student", student_id))

    users.extend([
        ("manager01", generate_password_hash("manager123"), "management", None),
        ("admin01", generate_password_hash("admin123"), "admin", None),
    ])

    for user in users:
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role, student_id) VALUES (?, ?, ?, ?)",
                user,
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

    print(f"Created/verified {len(students)} student accounts plus management and admin accounts.")


if __name__ == "__main__":
    create_database()
