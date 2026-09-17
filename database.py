import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "hospital.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _h(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'patient',
        email TEXT,
        phone TEXT,
        created_at TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_name TEXT,
        age INTEGER,
        phone TEXT,
        dept TEXT,
        doctor TEXT,
        appt_date TEXT,
        appt_time TEXT,
        reason TEXT,
        status TEXT DEFAULT 'Pending',
        payment_status TEXT DEFAULT 'Unpaid',
        amount INTEGER DEFAULT 0,
        created_at TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS lab_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_name TEXT,
        test_name TEXT,
        result TEXT,
        normal_range TEXT,
        status TEXT DEFAULT 'Normal',
        report_date TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_name TEXT,
        description TEXT,
        amount INTEGER,
        status TEXT DEFAULT 'Unpaid',
        bill_date TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        recipient TEXT,
        subject TEXT,
        message TEXT,
        sent_at TEXT
    )""")

    conn.commit()

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.executemany(
            "INSERT INTO users (username, password, role, email, phone, created_at) VALUES (?,?,?,?,?,?)",
            [
                ("admin", _h("admin123"), "admin", "admin@almuzamil.pk", "0317-8377873", now),
                ("patient", _h("patient123"), "patient", "patient@example.com", "0300-0000000", now),
                ("doctor", _h("doctor123"), "doctor", "doctor@almuzamil.pk", "0300-1111111", now),
            ]
        )
        conn.commit()
    conn.close()

def create_user(username, password, email="", phone="", role="patient"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, role, email, phone, created_at) VALUES (?,?,?,?,?,?)",
            (username, password, role, email, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_users():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, role, email, phone, created_at FROM users"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_appointment(user_id, patient_name, age, phone, dept, doctor,
                    appt_date, appt_time, reason, amount):
    conn = get_connection()
    conn.execute("""
        INSERT INTO appointments
        (user_id, patient_name, age, phone, dept, doctor, appt_date, appt_time,
         reason, status, payment_status, amount, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (user_id, patient_name, age, phone, dept, doctor, appt_date, appt_time,
          reason, "Pending", "Unpaid", amount,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_appointments_by_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM appointments WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_appointments():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM appointments ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_appointment_status(appt_id, status=None, payment_status=None):
    conn = get_connection()
    if status:
        conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, appt_id))
    if payment_status:
        conn.execute(
            "UPDATE appointments SET payment_status=? WHERE id=?",
            (payment_status, appt_id)
        )
    conn.commit()
    conn.close()

def get_doctor_schedule(doctor):
    conn = get_connection()
    rows = conn.execute(
        """SELECT appt_date, appt_time, patient_name, status
           FROM appointments WHERE doctor=?
           ORDER BY appt_date, appt_time""",
        (doctor,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_lab_report(user_id, patient_name, test_name, result, normal_range, status):
    conn = get_connection()
    conn.execute("""
        INSERT INTO lab_reports
        (user_id, patient_name, test_name, result, normal_range, status, report_date)
        VALUES (?,?,?,?,?,?,?)
    """, (user_id, patient_name, test_name, result, normal_range, status,
          datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_lab_reports(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM lab_reports WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM lab_reports ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_bill(user_id, patient_name, description, amount):
    conn = get_connection()
    conn.execute("""
        INSERT INTO bills
        (user_id, patient_name, description, amount, status, bill_date)
        VALUES (?,?,?,?,?,?)
    """, (user_id, patient_name, description, amount, "Unpaid",
          datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_bills(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM bills WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM bills ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def pay_bill(bill_id):
    conn = get_connection()
    conn.execute("UPDATE bills SET status='Paid' WHERE id=?", (bill_id,))
    conn.commit()
    conn.close()

def log_notification(user_id, recipient, subject, message):
    conn = get_connection()
    conn.execute("""
        INSERT INTO notifications
        (user_id, recipient, subject, message, sent_at)
        VALUES (?,?,?,?,?)
    """, (user_id, recipient, subject, message,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_notifications(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM notifications ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
