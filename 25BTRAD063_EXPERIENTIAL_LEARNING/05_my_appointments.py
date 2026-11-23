# NAME   : Manu R
# USN    : 25BTRAD063
# BRANCH : CSE – AIDE A
# PROJECT: Hospital Appointment Management System (Python + Tkinter + SQLite)
# Program 5: My Appointments (Search and Cancel)

"""
Tkinter window where a patient enters their registered phone number to view
their appointments and cancel a booked one.
Run: python 05_my_appointments.py
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

    def patient_appointments(self, phone):
        return self.conn.execute("""
            SELECT a.appointment_id, d.name, d.specialization,
                   a.appointment_date, a.appointment_time, a.status
            FROM appointments a
            JOIN patients p ON p.patient_id=a.patient_id
            JOIN doctors d ON d.doctor_id=a.doctor_id
            WHERE p.phone=?
            ORDER BY a.appointment_date, a.appointment_time
        """, (phone,)).fetchall()

    def cancel_patient_appointment(self, appointment_id, phone):
        cur = self.conn.execute("""
            UPDATE appointments SET status='Cancelled'
            WHERE appointment_id=? AND patient_id=
                (SELECT patient_id FROM patients WHERE phone=?)
                AND status='Booked'
        """, (appointment_id, phone))
        self.conn.commit()
        return cur.rowcount

    def close(self):
        self.conn.close()


class MyAppointmentsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Appointments")
        self.root.geometry("900x500")
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
        ttk.Label(self.frame, text="Find Your Appointments",
                  font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 10))
        bar = ttk.Frame(self.frame)
        bar.pack(fill="x", pady=(0, 12))
        ttk.Label(bar, text="Registered phone number:").pack(side="left")
        self.lookup_phone = tk.StringVar()
        ttk.Entry(bar, textvariable=self.lookup_phone, width=25).pack(side="left", padx=8)
        ttk.Button(bar, text="Search", command=self.search_appointments).pack(side="left")
        cols = ("id", "doctor", "specialty", "date", "time", "status")
        self.appt_tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=12)
        for col, title, width in [
            ("id", "Appointment ID", 100), ("doctor", "Doctor", 180),
            ("specialty", "Specialization", 170), ("date", "Date", 110),
            ("time", "Time", 100), ("status", "Status", 100)
        ]:
            self.appt_tree.heading(col, text=title)
            self.appt_tree.column(col, width=width, anchor="w")
        self.appt_tree.pack(fill="both", expand=True)
        ttk.Button(self.frame, text="Cancel Selected Appointment",
                   command=self.cancel_appointment).pack(anchor="e", pady=10)

    def search_appointments(self):
        phone = self.lookup_phone.get().strip()
        if not phone:
            messagebox.showwarning("Phone required", "Enter your registered phone number.")
            return
        for item in self.appt_tree.get_children():
            self.appt_tree.delete(item)
        rows = self.db.patient_appointments(phone)
        for row in rows:
            self.appt_tree.insert("", "end", values=row)
        if not rows:
            messagebox.showinfo("No records", "No appointments were found for this phone number.")

    def cancel_appointment(self):
        selected = self.appt_tree.selection()
        if not selected:
            messagebox.showwarning("Select appointment", "Select an appointment to cancel.")
            return
        values = self.appt_tree.item(selected[0], "values")
        appt_id = values[0]
        if values[5] != "Booked":
            messagebox.showinfo("Cannot cancel", "Only booked appointments can be cancelled.")
            return
        if messagebox.askyesno("Confirm cancellation", f"Cancel appointment {appt_id}?"):
            changed = self.db.cancel_patient_appointment(appt_id, self.lookup_phone.get().strip())
            if changed:
                messagebox.showinfo("Cancelled", "Appointment cancelled successfully.")
                self.search_appointments()
            else:
                messagebox.showerror("Error", "The appointment could not be cancelled.")

    def on_close(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MyAppointmentsApp(root)
    root.mainloop()
