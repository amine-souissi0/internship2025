# db_setup.py

import os
import sqlite3
from config import Config
from app.models.user import User
from cryptography.fernet import Fernet


def init_db():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            employee_id INTEGER,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            role TEXT NOT NULL DEFAULT 'adc_employee',
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
        )
    ''')

    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            team TEXT,
            total_overtime TEXT DEFAULT '00:00'
        )
    ''')

    # Create shifts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_time,
            end_time,
            bg_color TEXT NOT NULL,
            text_color TEXT DEFAULT '#000000',
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
    ''')

    # Create employee_shift table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_shift (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            shift_id INTEGER NOT NULL,
            date DATE NOT NULL,
            actual_start_time TIME,
            actual_end_time TIME,
            overtime_hours TEXT DEFAULT '00:00',
            request_status TEXT DEFAULT 'NONE',
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (shift_id) REFERENCES shifts(id)
        )
    ''')

    conn.commit()
    conn.close()


def print_db():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
        
    names = cursor.fetchall()
    for name in names:
        print(name)
    
    for table in ["users", "employees", "shifts", "employee_shift"]:
        # Print table schema
        cursor.execute(f"PRAGMA table_info({table})")
        schema = cursor.fetchall()
        print(f"Schema {table}:")
        for column in schema:
            print(f"Column: {column[1]}, Type: {column[2]}")

        # Print table data
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()
        print(f"\nTable {table}:")
        for row in data:
            print(row)

        print("\n_______________________________________\n")

    conn.close()


def modify_db():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()

    try:
        # # Step 1: Create the new shifts table
        # cursor.execute('''
        # CREATE TABLE IF NOT EXISTS new_shifts (
        #     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     name TEXT NOT NULL,
        #     start_time TEXT,
        #     end_time TEXT,
        #     bg_color TEXT NOT NULL,
        #     text_color TEXT DEFAULT '#000000',
        #     is_active BOOLEAN NOT NULL DEFAULT 1
        # )
        # ''')

        # # Step 2: Copy data from the old table to the new table
        # cursor.execute('''
        # INSERT INTO new_shifts (id, name, start_time, end_time, bg_color, is_active)
        # SELECT id, name, start_time, end_time, rgb, is_active
        # FROM shifts
        # ''')

        # # Step 3: Drop the old shifts table
        # cursor.execute('DROP TABLE shifts')

        # # Step 4: Rename the new table to shifts
        # cursor.execute('ALTER TABLE new_shifts RENAME TO shifts')

        cursor.execute('DELETE FROM employee_shift WHERE id = 117')
        conn.commit()
        print("Successfully updated the shifts table structure.")
    except Exception as e:
        conn.rollback()
        print(f"Error cleaning orphaned shifts: {str(e)}")
    finally:
        conn.close()
        

if __name__ == '__main__':
    # init_db()
    modify_db()
    print_db()
