"""
MedEase - Hospital Appointment Management System
Python + Tkinter + SQLite

Experiential Learning - Python Team Project
Class: AIDE A  |  Institution: Jain University

Team members:
    1. HARSHITH       - USN 25BTRAD040
    2. MANU           - USN 25BTRAD063
    3. VIJESH         - USN 25BTRAD04G
    4. EDWARD PHILIP  - USN 25BTRAD032
    5. HARNISH        - USN 25BTRAD016

Run: python main.py
Demo administrator: username=admin, password=admin123
This is an educational demonstration, not a production hospital system.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date

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

    def register_patient(self, name, age, gender, phone):
        cur = self.conn.execute(
            "INSERT INTO patients(name, age, gender, phone) VALUES (?, ?, ?, ?)",
            (name, age, gender, phone)
        )
        self.conn.commit()
        return cur.lastrowid

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
        cur = self.conn.execute(
            """INSERT INTO appointments
               (patient_id, doctor_id, appointment_date, appointment_time)
               VALUES (?, ?, ?, ?)""",
            (patient_id, doctor_id, appt_date, appt_time)
        )
        self.conn.commit()
        return cur.lastrowid

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


class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MedEase")
        self.root.geometry("1000x680")
        self.root.minsize(850, 600)
        self.db = HospitalDB()
        self.doctor_map = {}
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Title.TLabel", font=("Arial", 20, "bold"))
        self.style.configure("Sub.TLabel", font=("Arial", 10))
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        header = ttk.Frame(self.root, padding=16)
        header.pack(fill="x")
        ttk.Label(header, text="MedEase",
                  style="Title.TLabel").pack()
        ttk.Label(header, text="Patient registration • Doctor directory • Appointment booking",
                  style="Sub.TLabel").pack(pady=(5, 0))

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.patient_tab = ttk.Frame(self.tabs, padding=16)
        self.doctor_tab = ttk.Frame(self.tabs, padding=16)
        self.booking_tab = ttk.Frame(self.tabs, padding=16)
        self.lookup_tab = ttk.Frame(self.tabs, padding=16)
        self.tabs.add(self.patient_tab, text="Patient Registration")
        self.tabs.add(self.doctor_tab, text="Doctors")
        self.tabs.add(self.booking_tab, text="Book Appointment")
        self.tabs.add(self.lookup_tab, text="My Appointments")

        self.build_patient_tab()
        self.build_doctor_tab()
        self.build_booking_tab()
        self.build_lookup_tab()

        footer = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        footer.pack(fill="x")
        ttk.Button(footer, text="Administrator Login", command=self.admin_login).pack(side="left")
        ttk.Label(footer, text="Educational project — use sample data only",
                  foreground="#666").pack(side="right")

    def build_patient_tab(self):
        ttk.Label(self.patient_tab, text="Register a Patient",
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
            ttk.Label(self.patient_tab, text=label).grid(row=i, column=0, sticky="w", pady=8)
            ttk.Entry(self.patient_tab, textvariable=var, width=38).grid(row=i, column=1, sticky="w", pady=8)
        ttk.Label(self.patient_tab, text="Gender").grid(row=4, column=0, sticky="w", pady=8)
        ttk.Combobox(self.patient_tab, textvariable=self.p_gender,
                     values=["Female", "Male", "Other", "Prefer not to say"],
                     state="readonly", width=35).grid(row=4, column=1, sticky="w", pady=8)
        ttk.Button(self.patient_tab, text="Register Patient",
                   command=self.register_patient).grid(row=5, column=1, sticky="w", pady=16)
        ttk.Label(self.patient_tab,
                  text="Use a unique phone number. The phone number is used to find your appointments.",
                  wraplength=650).grid(row=6, column=0, columnspan=2, sticky="w", pady=10)

    def build_doctor_tab(self):
        ttk.Label(self.doctor_tab, text="Available Doctors",
                  font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 12))
        columns = ("id", "name", "specialization", "availability")
        self.doctor_tree = ttk.Treeview(self.doctor_tab, columns=columns, show="headings", height=14)
        headings = [("id", "ID", 60), ("name", "Doctor Name", 220),
                    ("specialization", "Specialization", 220),
                    ("availability", "Consultation Hours", 240)]
        for col, title, width in headings:
            self.doctor_tree.heading(col, text=title)
            self.doctor_tree.column(col, width=width, anchor="w")
        self.doctor_tree.pack(fill="both", expand=True)
        ttk.Button(self.doctor_tab, text="Refresh Doctor List",
                   command=self.refresh_doctors).pack(anchor="e", pady=10)
        self.refresh_doctors()

    def build_booking_tab(self):
        ttk.Label(self.booking_tab, text="Book an Appointment",
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
            ttk.Label(self.booking_tab, text=label).grid(row=i, column=0, sticky="w", pady=9)
            ttk.Entry(self.booking_tab, textvariable=var, width=38).grid(row=i, column=1, sticky="w", pady=9)
        ttk.Label(self.booking_tab, text="Doctor").grid(row=3, column=0, sticky="w", pady=9)
        self.doctor_combo = ttk.Combobox(self.booking_tab, textvariable=self.b_doctor,
                                         state="readonly", width=35)
        self.doctor_combo.grid(row=3, column=1, sticky="w", pady=9)
        ttk.Label(self.booking_tab, text="Time slot").grid(row=4, column=0, sticky="w", pady=9)
        ttk.Combobox(self.booking_tab, textvariable=self.b_time, values=TIME_SLOTS,
                     state="readonly", width=35).grid(row=4, column=1, sticky="w", pady=9)
        ttk.Button(self.booking_tab, text="Book Appointment",
                   command=self.book_appointment).grid(row=5, column=1, sticky="w", pady=16)
        ttk.Label(self.booking_tab,
                  text="Appointments can be booked for today or a future date. A doctor/time slot can only be booked once.",
                  wraplength=700).grid(row=6, column=0, columnspan=2, sticky="w", pady=8)
        self.refresh_doctors()

    def build_lookup_tab(self):
        ttk.Label(self.lookup_tab, text="Find Your Appointments",
                  font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 10))
        bar = ttk.Frame(self.lookup_tab)
        bar.pack(fill="x", pady=(0, 12))
        ttk.Label(bar, text="Registered phone number:").pack(side="left")
        self.lookup_phone = tk.StringVar()
        ttk.Entry(bar, textvariable=self.lookup_phone, width=25).pack(side="left", padx=8)
        ttk.Button(bar, text="Search", command=self.search_appointments).pack(side="left")
        cols = ("id", "doctor", "specialty", "date", "time", "status")
        self.appt_tree = ttk.Treeview(self.lookup_tab, columns=cols, show="headings", height=12)
        for col, title, width in [
            ("id", "Appointment ID", 100), ("doctor", "Doctor", 180),
            ("specialty", "Specialization", 170), ("date", "Date", 110),
            ("time", "Time", 100), ("status", "Status", 100)
        ]:
            self.appt_tree.heading(col, text=title)
            self.appt_tree.column(col, width=width, anchor="w")
        self.appt_tree.pack(fill="both", expand=True)
        ttk.Button(self.lookup_tab, text="Cancel Selected Appointment",
                   command=self.cancel_appointment).pack(anchor="e", pady=10)

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
            self.p_name.set(""); self.p_age.set(""); self.p_phone.set("")
            self.p_gender.set("Select")
        except sqlite3.IntegrityError:
            messagebox.showerror("Already registered", "This phone number is already registered.")

    def refresh_doctors(self):
        for item in self.doctor_tree.get_children():
            self.doctor_tree.delete(item)
        self.doctor_map.clear()
        doctors = self.db.get_doctors()
        for doctor_id, name, specialty, availability in doctors:
            self.doctor_tree.insert("", "end", values=(doctor_id, name, specialty, availability))
            self.doctor_map[f"{name} — {specialty} (ID {doctor_id})"] = doctor_id
        if hasattr(self, "doctor_combo"):
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
            self.lookup_phone.set(phone)
            self.search_appointments()
            self.b_date.set("")
        except sqlite3.IntegrityError:
            messagebox.showerror("Slot unavailable",
                                 "This doctor's selected time slot is already booked. Please choose another slot.")

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

    def admin_login(self):
        username = simpledialog.askstring("Administrator Login", "Username:")
        if username is None:
            return
        password = simpledialog.askstring("Administrator Login", "Password:", show="*")
        if password is None:
            return
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.open_admin_window()
        else:
            messagebox.showerror("Login failed", "Incorrect administrator username or password.")

    def open_admin_window(self):
        win = tk.Toplevel(self.root)
        win.title("Administrator Dashboard")
        win.geometry("1050x550")
        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Administrator — All Appointments",
                  font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 12))
        cols = ("id", "patient", "phone", "doctor", "specialty", "date", "time", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        specs = [("id", "Appt ID", 65), ("patient", "Patient", 130),
                 ("phone", "Phone", 110), ("doctor", "Doctor", 130),
                 ("specialty", "Specialization", 130), ("date", "Date", 95),
                 ("time", "Time", 90), ("status", "Status", 85)]
        for col, title, width in specs:
            tree.heading(col, text=title); tree.column(col, width=width, anchor="w")
        tree.pack(fill="both", expand=True)

        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            for row in self.db.all_appointments():
                tree.insert("", "end", values=row)

        def add_doctor():
            name = simpledialog.askstring("Add Doctor", "Doctor name:", parent=win)
            if not name or not name.strip(): return
            specialty = simpledialog.askstring("Add Doctor", "Specialization:", parent=win)
            if not specialty or not specialty.strip(): return
            hours = simpledialog.askstring("Add Doctor", "Availability (e.g. 09:00 AM - 01:00 PM):", parent=win)
            if not hours or not hours.strip(): return
            self.db.add_doctor(name.strip(), specialty.strip(), hours.strip())
            self.refresh_doctors()
            messagebox.showinfo("Success", "Doctor added successfully.", parent=win)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=10)
        ttk.Button(buttons, text="Refresh Records", command=refresh).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Add Doctor", command=add_doctor).pack(side="left")
        refresh()

    def on_close(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()
