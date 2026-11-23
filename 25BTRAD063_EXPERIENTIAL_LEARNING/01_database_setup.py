# NAME   : Manu R
# USN    : 25BTRAD063
# BRANCH : CSE – AIDE A
# PROJECT: Hospital Appointment Management System (Python + Tkinter + SQLite)
# Program 1: Database Setup (SQLite tables and doctor seed data)

"""
Creates hospital.db with the patients, doctors and appointments tables,
adds the default doctors, and prints a summary.
Run: python 01_database_setup.py
"""

import sqlite3

DB_NAME = "hospital.db"

DOCTORS = [
    ("Dr. Ananya Rao", "General Medicine", "09:00 AM - 01:00 PM"),
    ("Dr. Rahul Sharma", "Cardiology", "10:00 AM - 02:00 PM"),
    ("Dr. Meera Nair", "Dermatology", "02:00 PM - 05:00 PM"),
    ("Dr. Arjun Kumar", "Orthopedics", "09:00 AM - 12:00 PM"),
    ("Dr. Priya Das", "Pediatrics", "11:00 AM - 03:00 PM"),
]


class HospitalDB:
    def __init__(self, filename=DB_NAME):
        self.conn = sqlite3.connect(filename)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()
        self.seed_doctors()

    def create_tables(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            availability TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Booked',
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id),
            UNIQUE(doctor_id, appointment_date, appointment_time)
        );
        """)
        self.conn.commit()

    def seed_doctors(self):
        count = self.conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        if count == 0:
            self.conn.executemany(
                "INSERT INTO doctors(name, specialization, availability) VALUES (?, ?, ?)",
                DOCTORS
            )
            self.conn.commit()

    def get_doctors(self):
        return self.conn.execute(
            "SELECT doctor_id, name, specialization, availability FROM doctors ORDER BY name"
        ).fetchall()

    def count(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    database = HospitalDB()

    print("===== HOSPITAL DATABASE SETUP =====")
    print("Database file :", DB_NAME)
    print("Tables ready  : patients, doctors, appointments\n")

    print("{:<4} {:<20} {:<18} {}".format("ID", "Doctor", "Specialization", "Consultation Hours"))
    print("-" * 70)
    for doctor_id, name, specialty, availability in database.get_doctors():
        print("{:<4} {:<20} {:<18} {}".format(doctor_id, name, specialty, availability))

    print("\nRecords stored:")
    print("  Patients     :", database.count("patients"))
    print("  Doctors      :", database.count("doctors"))
    print("  Appointments :", database.count("appointments"))

    database.close()
