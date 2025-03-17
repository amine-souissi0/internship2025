# app/services/employee_service.py

"""
Employee Service

This module provides functions for managing employee data:
- get_all_employees: Retrieve all employees
- get_employee_by_id: Get a specific employee by ID
- get_all_employees_with_users: Get employees with associated user data
- add_employee: Add a new employee
- delete_employee: Remove an employee
- update_employee: Update employee details
- save_new_password: Update an employee's password
- update_user_role: Update an employee's role
"""

from app.database.db import get_db
from app.models.employee import Employee

def get_all_employees():
    db = get_db()
    try:
        rows = db.execute('SELECT * FROM employees').fetchall()
        return [Employee(row['first_name'], row['last_name'], row['team'], row['id']) for row in rows]
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return []
    finally:
        db.close()

def get_employee_by_id(id):
    db = get_db()
    try:
        row = db.execute('SELECT * FROM employees WHERE id = ?',(id,)).fetchone()
        if row:
            return Employee(row['first_name'], row['last_name'], row['team'], row['id'])
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return []
    finally:
        db.close()
        
        
def get_all_employees_with_users():
    db = get_db()
    try:
        query = '''
        SELECT e.*, u.id AS user_id, u.username, u.password_hash, u.role
        FROM employees e
        LEFT JOIN users u ON e.id = u.employee_id
        '''
        rows = db.execute(query).fetchall()
        return [
            {
                'employee': Employee(row['first_name'], row['last_name'], row['team'], row['id']),
                'user_id': row['user_id'],
                'username': row['username'],
                'password_hash': row['password_hash'],
                'role': row['role']
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error fetching employees with users: {e}")
        return []
    finally:
        db.close()

def add_employee(first_name, last_name, team):
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO employees (first_name, last_name, team) VALUES (?, ?, ?)',
                   (first_name, last_name, team))
        db.commit()
        employee_id = cursor.lastrowid
        return employee_id
    except Exception as e:
        db.rollback()
        print(f"Error adding employee: {e}")
        return None
    finally:
        db.close()

def delete_employee(id):
    db = get_db()
    try:
        db.execute('DELETE FROM employees WHERE id = ?', (id,))
        db.execute('DELETE FROM users WHERE employee_id = ?', (id,))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting employee: {e}")
        return False
    finally:
        db.close()


def update_employee(id, first_name, last_name, team):
    db = get_db()
    try:
        db.execute('UPDATE employees SET first_name = ?, last_name = ?, team = ? WHERE id = ?',
                   (first_name, last_name, team, id))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating employee: {e}")
        return False
    finally:
        db.close()
        
def save_new_password(password, id):
    print(f"Attempt saving password for user {id} with {password}")
    db = get_db()
    try:
        db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password, id))
        db.commit()
        print(f"Password updated for user {id} with {password}")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving new password: {e}")
        return False
    finally:
        db.close()
        
def update_user_role(user_id, new_role):
    db = get_db()
    try:
        db.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating user role: {e}")
        return False
    finally:
        db.close()
