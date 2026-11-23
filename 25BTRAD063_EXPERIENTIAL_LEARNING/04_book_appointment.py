# NAME   : Manu R
# USN    : 25BTRAD063
# BRANCH : CSE – AIDE A
# PROJECT: Hospital Appointment Management System (Python + Tkinter + SQLite)
# Program 4: Appointment Booking

"""
Tkinter form to book an appointment for a registered patient (found by phone
number). A doctor / date / time slot can only be booked once.
Register the patient first using 02_patient_registration.py.
Run: python 04_book_appointment.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

DB_NAME = "hospital.db"

DOCTORS = [
    ("Dr. Ananya Rao", "General Medicine", "09:00 AM - 01:00 PM"),
    ("Dr. Rahul Sharma", "Cardiology", "10:00 AM - 02:00 PM"),
    ("Dr. Meera Nair", "Dermatology", "02:00 PM - 05:00 PM"),
    ("Dr. Arjun Kumar", "Orthopedics", "09:00 AM - 12:00 PM"),
    ("Dr. Priya Das", "Pediatrics", "11:00 AM - 03:00 PM"),
]

TIME_SLOTS = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
              "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"]


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

    def get_patient_by_phone(self, phone):
        return self.conn.execute(
            "SELECT patient_id, name, age, gender, phone FROM patients WHERE phone=?",
            (phone,)
        ).fetchone()

    def get_doctors(self):
        return self.conn.execute(
            "SELECT doctor_id, name, specialization, availability FROM doctors ORDER BY name"
        ).fetchall()

    def book(self, patient_id, doctor_id, appt_date, appt_time):
        try:
            cur = self.conn.execute(
                """INSERT INTO appointments
                   (patient_id, doctor_id, appointment_date, appointment_time)
                   VALUES (?, ?, ?, ?)""",
                (patient_id, doctor_id, appt_date, appt_time)
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            self.conn.rollback()   # release the lock so other programs can use the database
            raise

    def close(self):
        self.conn.close()


class BookAppointmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book an Appointment")
        self.root.geometry("800x430")
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
        ttk.Label(f, text="Book an Appointment",
                  font=("Arial", 15, "bold")).grid(row=0, column=0, columnspan=2,
                                                   sticky="w", pady=(0, 14))
        self.b_phone = tk.StringVar()
        self.b_doctor = tk.StringVar()
        self.b_date = tk.StringVar()
        self.b_time = tk.StringVar(value=TIME_SLOTS[0])
        self.doctor_map = {}
        rows = [
            ("Registered phone number", self.b_phone),
            ("Appointment date (YYYY-MM-DD)", self.b_date),
        ]
        for i, (label, var) in enumerate(rows, start=1):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="w", pady=9)
            ttk.Entry(f, textvariable=var, width=38).grid(row=i, column=1, sticky="w", pady=9)
        ttk.Label(f, text="Doctor").grid(row=3, column=0, sticky="w", pady=9)
        self.doctor_combo = ttk.Combobox(f, textvariable=self.b_doctor,
                                         state="readonly", width=35)
        self.doctor_combo.grid(row=3, column=1, sticky="w", pady=9)
        ttk.Label(f, text="Time slot").grid(row=4, column=0, sticky="w", pady=9)
        ttk.Combobox(f, textvariable=self.b_time, values=TIME_SLOTS,
                     state="readonly", width=35).grid(row=4, column=1, sticky="w", pady=9)
        ttk.Button(f, text="Book Appointment",
                   command=self.book_appointment).grid(row=5, column=1, sticky="w", pady=16)
        ttk.Label(f,
                  text="Appointments can be booked for today or a future date. A doctor/time slot can only be booked once.",
                  wraplength=700).grid(row=6, column=0, columnspan=2, sticky="w", pady=8)
        self.load_doctors()

    def load_doctors(self):
        self.doctor_map.clear()
        for doctor_id, name, specialty, availability in self.db.get_doctors():
            self.doctor_map[f"{name} — {specialty} (ID {doctor_id})"] = doctor_id
        self.doctor_combo["values"] = list(self.doctor_map.keys())
        if self.doctor_map and not self.b_doctor.get():
            self.b_doctor.set(list(self.doctor_map.keys())[0])

    def book_appointment(self):
        phone = self.b_phone.get().strip()
        doctor_label = self.b_doctor.get()
        appt_date = self.b_date.get().strip()
        appt_time = self.b_time.get()
        if not all([phone, doctor_label, appt_date, appt_time]):
            messagebox.showwarning("Missing information", "Please complete all booking fields.")
            return
        patient = self.db.get_patient_by_phone(phone)
        if not patient:
            messagebox.showerror("Patient not found", "Please register using this phone number first.")
            return
        try:
            parsed = datetime.strptime(appt_date, "%Y-%m-%d").date()
            if parsed < date.today():
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid date", "Enter today's date or a future date in YYYY-MM-DD format.")
            return
        doctor_id = self.doctor_map.get(doctor_label)
        try:
            appt_id = self.db.book(patient[0], doctor_id, appt_date, appt_time)
            messagebox.showinfo("Appointment confirmed",
                                f"Appointment booked successfully!\n\nAppointment ID: {appt_id}\n"
                                f"Patient: {patient[1]}\nDoctor: {doctor_label}\n"
                                f"Date: {appt_date}\nTime: {appt_time}")
            self.b_date.set("")
        except sqlite3.IntegrityError:
            messagebox.showerror("Slot unavailable",
                                 "This doctor's selected time slot is already booked. Please choose another slot.")

    def on_close(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BookAppointmentApp(root)
    root.mainloop()
