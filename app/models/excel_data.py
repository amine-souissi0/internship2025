from app.database.db import get_db

def create_excel_data_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shift_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            full_name TEXT,
            shift_type TEXT
        )
    ''')
    conn.commit()
