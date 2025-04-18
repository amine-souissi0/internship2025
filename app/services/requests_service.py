# app/services/requests_service.py

"""
Requests Service

This module provides functions for managing shift requests:
- get_all_requests: Retrieve all shift requests
- update_request_status: Update the status of a request
- approve_request: Approve a shift request
- reject_request: Reject a shift request
"""

from app.database.db import get_db

def get_all_requests():
    db = get_db()
    try:
        rows = db.execute('''
            SELECT es.id, es.employee_id, es.shift_id, es.date, es.shift_type,
                   e.first_name || ' ' || e.last_name AS employee_name, 
                   s.name AS shift_name,
                   es.approval_status
            FROM employee_shift es
            JOIN employees e ON es.employee_id = e.id
            JOIN shifts s ON es.shift_id = s.id
            WHERE es.approval_status = 'Pending'
        ''').fetchall()
        requests = []
        for row in rows:
            requests.append({
                'id': row['id'],
                'employee_name': row['employee_name'],
                'shift_name': row['shift_name'],
                'date': row['date'],
                'shift_type': row['shift_type'],
                'approval_status': row['approval_status']
            })
        return requests
    except Exception as e:
        print(f"Error fetching requests: {e}")
        return []
    finally:
        db.close()

def update_request_status(id, approval_status):
    db = get_db()
    try:
        db.execute('UPDATE employee_shift SET approval_status = ? WHERE id = ?', (approval_status, id))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating request status: {e}")
        return False
    finally:
        db.close()

def approve_request(id):
    db = get_db()
    try:
        return update_request_status(id, "Approved")
    except Exception as e:
        db.rollback()
        print(f"Error approving request: {e}")
        return False
    finally:
        db.close()

def reject_request(id):
    db = get_db()
    try:
        # Delete the shift instead of just updating the status
        db.execute('DELETE FROM employee_shift WHERE id = ?', (id,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error rejecting request: {e}")
        db.rollback()
        return False
    finally:
        db.close()