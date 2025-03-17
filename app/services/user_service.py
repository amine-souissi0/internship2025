# app/services/user_service.py

from app.database.db import get_db
from app.models.user import User
from config import Config
from cryptography.fernet import Fernet


def create_user(username, password, employee_id=None, is_active=True, role='adc_employee'):
    db = get_db()
    try:
        print(f"Attempting to create user: {username}")
        existing_user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user is not None:
            print(f"User '{username}' already exists. User data: {existing_user}")
            return False

        fernet = Fernet(Config.ENCRYPTION_KEY)
        encrypted_password = fernet.encrypt(password.encode()).decode()
        db.execute(
            'INSERT INTO users (username, password_hash, employee_id, is_active, role) VALUES (?, ?, ?, ?, ?)',
            (username, encrypted_password, employee_id, is_active, role))
        db.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        db.close()

def get_user_by_username(username):
    db = get_db()
    try:
        row = db.execute('SELECT * FROM users WHERE username = ?', (username, )).fetchone()

        print(f"get_user_by_username(username) {username}")
        print("row", row)
        if row:
            print(f"Raw password hash: {row[2]}")
            print(f"User data: id={row[0]}, username={row[1]}, employee_id={row[3]}, is_active={row[4]}, role={row[5]}")
            return User(row[0], row[1], row[2], row[3], row[4], row[5])
        print("get_user_by_username: User not found")
        pass
    except Exception as e:
        print(f"Error getting user by username: {e}")
        return False
    finally:
        db.close()

def get_user_by_id(user_id):
    db = get_db()
    try:
        row = db.execute('SELECT * FROM users WHERE id = ?', (user_id, )).fetchone()
        if row:
            print(f"User data: id={row[0]}, username={row[1]}, employee_id={row[3]}, is_active={row[4]}, role={row[5]}")
            return User(row[0], row[1], row[2], row[3], row[4], row[5])
    except Exception as e:
        print("get_user_by_id: User not found")
        return False
    finally:
        db.close()