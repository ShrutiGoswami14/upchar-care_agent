"""SQLite clinic database: schema + deterministic seed data."""
import sqlite3
from pathlib import Path

import os

PROJECT_DIR = Path(__file__).parent

PROJECT_DIR = Path(__file__).parent

if os.getenv("EVAL_MODE") == "1":
    DB_PATH = PROJECT_DIR / "clinic_eval.db"
else:
    DB_PATH = PROJECT_DIR / "clinic.db"
DOCTORS = [
    (1, "Dr. Anita Rao", "Cardiology"),
    (2, "Dr. Vikram Sen", "General Physician"),
    (3, "Dr. Meera Das", "Dermatology"),
    (4, "Dr. Arjun Roy", "Pediatrics"),
]
DATES = ["2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15", "2026-10-16"]
TIMES = ["10:00", "11:00", "15:00"]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset():
    """Drop and re-create all tables with the same data every time (needed for repeatable evals)."""
    conn = connect()
    conn.executescript(
        """
        DROP TABLE IF EXISTS appointments;
        DROP TABLE IF EXISTS slots;
        DROP TABLE IF EXISTS doctors;
        CREATE TABLE doctors (id INTEGER PRIMARY KEY, name TEXT, specialty TEXT);
        CREATE TABLE slots (doctor_id INTEGER, date TEXT, time TEXT, booked INTEGER DEFAULT 0,
                            PRIMARY KEY (doctor_id, date, time));
        CREATE TABLE appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_name TEXT,
                            doctor_id INTEGER, date TEXT, time TEXT, status TEXT DEFAULT 'confirmed');
        """
    )
    conn.executemany("INSERT INTO doctors VALUES (?,?,?)", DOCTORS)
    for d_id, _, _ in DOCTORS:
        for date in DATES:
            for t in TIMES:
                conn.execute("INSERT INTO slots VALUES (?,?,?,0)", (d_id, date, t))
    # One pre-booked appointment (id 1) so cancel/lookup cases have something to act on
    conn.execute("INSERT INTO appointments (patient_name, doctor_id, date, time) VALUES ('Ravi Kumar', 2, '2026-10-12', '10:00')")
    conn.execute("UPDATE slots SET booked=1 WHERE doctor_id=2 AND date='2026-10-12' AND time='10:00'")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    reset()
    print("Database seeded:", DB_PATH)
