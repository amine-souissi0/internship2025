# app/models/shift_log.py
from app.database.db import get_db

def create_shift_log_table():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS shift_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            full_name TEXT,
            date TEXT,
            shift_type TEXT
        )
    ''')
    db.commit()
