# NAME   : Manu R
# USN    : 25BTRAD063
# BRANCH : CSE – AIDE A
# PROJECT: Hospital Appointment Management System (Python + Tkinter + SQLite)
# Program 6: Administrator Login and Dashboard

"""
Administrator login followed by a dashboard that shows all appointments and
lets the administrator add new doctors.
Demo administrator: username=admin, password=admin123
This is an educational demonstration, not a production hospital system.
Run: python 06_admin_dashboard.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DB_NAME = "hospital.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

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

    def all_appointments(self):
        return self.conn.execute("""
            SELECT a.appointment_id, p.name, p.phone, d.name,
                   d.specialization, a.appointment_date,
                   a.appointment_time, a.status
            FROM appointments a
            JOIN patients p ON p.patient_id=a.patient_id
            JOIN doctors d ON d.doctor_id=a.doctor_id
            ORDER BY a.appointment_date, a.appointment_time
        """).fetchall()

    def add_doctor(self, name, specialization, availability):
        self.conn.execute(
            "INSERT INTO doctors(name, specialization, availability) VALUES (?, ?, ?)",
            (name, specialization, availability)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


def admin_login(root):
    username = simpledialog.askstring("Administrator Login", "Username:", parent=root)
    if username is None:
        return False
    password = simpledialog.askstring("Administrator Login", "Password:", show="*", parent=root)
    if password is None:
        return False
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True
    messagebox.showerror("Login failed", "Incorrect administrator username or password.")
    return False


class AdminDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrator Dashboard")
        self.root.geometry("1050x550")
        self.db = HospitalDB()
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.frame = ttk.Frame(self.root, padding=14)
        self.frame.pack(fill="both", expand=True)
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        frame = self.frame
        ttk.Label(frame, text="Administrator — All Appointments",
                  font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 12))
        cols = ("id", "patient", "phone", "doctor", "specialty", "date", "time", "status")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        specs = [("id", "Appt ID", 65), ("patient", "Patient", 130),
                 ("phone", "Phone", 110), ("doctor", "Doctor", 130),
                 ("specialty", "Specialization", 130), ("date", "Date", 95),
                 ("time", "Time", 90), ("status", "Status", 85)]
        for col, title, width in specs:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=10)
        ttk.Button(buttons, text="Refresh Records", command=self.refresh).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Add Doctor", command=self.add_doctor).pack(side="left")
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.db.all_appointments():
            self.tree.insert("", "end", values=row)

    def add_doctor(self):
        name = simpledialog.askstring("Add Doctor", "Doctor name:", parent=self.root)
        if not name or not name.strip():
            return
        specialty = simpledialog.askstring("Add Doctor", "Specialization:", parent=self.root)
        if not specialty or not specialty.strip():
            return
        hours = simpledialog.askstring("Add Doctor", "Availability (e.g. 09:00 AM - 01:00 PM):", parent=self.root)
        if not hours or not hours.strip():
            return
        self.db.add_doctor(name.strip(), specialty.strip(), hours.strip())
        messagebox.showinfo("Success", "Doctor added successfully.", parent=self.root)

    def on_close(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    if admin_login(root):
        root.deiconify()
        app = AdminDashboardApp(root)
        root.mainloop()
    else:
        root.destroy()
