# NAME   : Manu R
# USN    : 25BTRAD063
# BRANCH : CSE – AIDE A
# PROJECT: Hospital Appointment Management System (Python + Tkinter + SQLite)
# Program 3: Doctor Directory

"""
Tkinter window that lists all doctors with their specialization and
consultation hours.
Run: python 03_doctor_directory.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk

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

    def close(self):
        self.conn.close()


class DoctorDirectoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doctor Directory")
        self.root.geometry("850x480")
        self.db = HospitalDB()
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.frame = ttk.Frame(self.root, padding=16)
        self.frame.pack(fill="both", expand=True)
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        ttk.Label(self.frame, text="Available Doctors",
                  font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 12))
        columns = ("id", "name", "specialization", "availability")
        self.doctor_tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=14)
        headings = [("id", "ID", 60), ("name", "Doctor Name", 220),
                    ("specialization", "Specialization", 220),
                    ("availability", "Consultation Hours", 240)]
        for col, title, width in headings:
            self.doctor_tree.heading(col, text=title)
            self.doctor_tree.column(col, width=width, anchor="w")
        self.doctor_tree.pack(fill="both", expand=True)
        ttk.Button(self.frame, text="Refresh Doctor List",
                   command=self.refresh_doctors).pack(anchor="e", pady=10)
        self.refresh_doctors()

    def refresh_doctors(self):
        for item in self.doctor_tree.get_children():
            self.doctor_tree.delete(item)
        for doctor_id, name, specialty, availability in self.db.get_doctors():
            self.doctor_tree.insert("", "end", values=(doctor_id, name, specialty, availability))

    def on_close(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DoctorDirectoryApp(root)
    root.mainloop()
