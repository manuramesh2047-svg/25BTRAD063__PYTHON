# NAME   : Manu R
# USN    : 25BTRAD063
# BRANCH : CSE – AIDE A
# PROJECT: Hospital Appointment Management System (Python + Tkinter + SQLite)
# Program 2: Patient Registration

"""
Tkinter form to register a patient (name, age, gender, unique phone number).
Run: python 02_patient_registration.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

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

    def register_patient(self, name, age, gender, phone):
        try:
            cur = self.conn.execute(
                "INSERT INTO patients(name, age, gender, phone) VALUES (?, ?, ?, ?)",
                (name, age, gender, phone)
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            self.conn.rollback()   # release the lock so other programs can use the database
            raise

    def close(self):
        self.conn.close()


class PatientRegistrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Patient Registration")
        self.root.geometry("700x420")
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
        f = self.frame
        ttk.Label(f, text="Register a Patient",
                  font=("Arial", 15, "bold")).grid(row=0, column=0, columnspan=2,
                                                   sticky="w", pady=(0, 14))
        self.p_name = tk.StringVar()
        self.p_age = tk.StringVar()
        self.p_gender = tk.StringVar(value="Select")
        self.p_phone = tk.StringVar()
        fields = [
            ("Full name", self.p_name),
            ("Age", self.p_age),
            ("Phone number", self.p_phone),
        ]
        for i, (label, var) in enumerate(fields, start=1):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="w", pady=8)
            ttk.Entry(f, textvariable=var, width=38).grid(row=i, column=1, sticky="w", pady=8)
        ttk.Label(f, text="Gender").grid(row=4, column=0, sticky="w", pady=8)
        ttk.Combobox(f, textvariable=self.p_gender,
                     values=["Female", "Male", "Other", "Prefer not to say"],
                     state="readonly", width=35).grid(row=4, column=1, sticky="w", pady=8)
        ttk.Button(f, text="Register Patient",
                   command=self.register_patient).grid(row=5, column=1, sticky="w", pady=16)
        ttk.Label(f,
                  text="Use a unique phone number. The phone number is used to find your appointments.",
                  wraplength=650).grid(row=6, column=0, columnspan=2, sticky="w", pady=10)

    def register_patient(self):
        name, age, gender, phone = (self.p_name.get().strip(), self.p_age.get().strip(),
                                    self.p_gender.get(), self.p_phone.get().strip())
        if not name or not age or not phone or gender == "Select":
            messagebox.showwarning("Missing information", "Please complete all fields.")
            return
        if not age.isdigit() or not 1 <= int(age) <= 120:
            messagebox.showwarning("Invalid age", "Enter an age between 1 and 120.")
            return
        if not phone.isdigit() or not 8 <= len(phone) <= 15:
            messagebox.showwarning("Invalid phone", "Enter a phone number containing 8 to 15 digits.")
            return
        try:
            patient_id = self.db.register_patient(name, int(age), gender, phone)
            messagebox.showinfo("Registration successful",
                                f"Patient registered successfully.\nYour Patient ID is {patient_id}.")
            self.p_name.set("")
            self.p_age.set("")
            self.p_phone.set("")
            self.p_gender.set("Select")
        except sqlite3.IntegrityError:
            messagebox.showerror("Already registered", "This phone number is already registered.")

    def on_close(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PatientRegistrationApp(root)
    root.mainloop()
