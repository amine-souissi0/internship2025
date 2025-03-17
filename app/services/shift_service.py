# app/services/shift_service.py

"""
Shift Service

This module provides functions for managing shifts:
- get_all_shifts: Retrieve all shifts
- get_all_active_shifts: Retrieve all active shifts
- add_shift: Add a new shift
- delete_shift: Remove a shift
- update_shift: Update shift details
- toggle_active_shift: Toggle a shift's active status
"""


from app.database.db import get_db
from app.models.shift import Shift  # Import the Shift model


def get_all_shifts():
    db = get_db()
    try:
        rows = db.execute('SELECT * FROM shifts').fetchall()
        return [
            Shift(row['name'], row['bg_color'], row['text_color'], row['start_time'], row['end_time'],
                  row['id'], row['is_active']) for row in rows
        ]
    except Exception as e:
        print(f"Error fetching shifts: {e}")
        return []
    finally:
        db.close()
        
def get_all_active_shifts():
    db = get_db()
    try:
        rows = db.execute('SELECT * FROM shifts WHERE is_active = 1').fetchall()
        return [Shift(row['name'], row['bg_color'], row['text_color'], row['start_time'], row['end_time'], 
                      row['id'], row['is_active']) for row in rows]
    except Exception as e:
        print(f"Error fetching active shifts: {e}")
        return []
    finally:
        db.close()


def add_shift(name, bg_color, text_color, start_time=None, end_time=None):
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO shifts (name, bg_color, text_color, start_time, end_time) VALUES (?, ?, ?, ?, ?)',
            (name, bg_color, text_color, start_time, end_time))
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        print(f"Error adding shift: {e}")
        return None
    finally:
        db.close()


def delete_shift(id):
    db = get_db()
    try:
        db.execute('DELETE FROM shifts WHERE id = ?', (id, ))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting shift: {e}")
        return False
    finally:
        db.close()


def update_shift(shift_id, name, bg_color, text_color, start_time, end_time):
    db = get_db()
    try:
        db.execute(
            'UPDATE shifts SET name = ?, bg_color = ?, text_color = ?, start_time = ?, end_time = ? WHERE id = ?',
            (name, bg_color, text_color, start_time, end_time, shift_id))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating shift: {e}")
        return False
    finally:
        db.close()


def toggle_active_shift(id):
    db = get_db()
    try:
        db.execute('UPDATE shifts SET is_active = NOT is_active WHERE id = ?', (id,))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error toggling shift: {e}")
    finally:
        db.close()
