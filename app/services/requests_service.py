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
from app.models.employee_shift import EmployeeShift
from datetime import datetime

def get_all_requests():
    db = get_db()
    try:
        rows = db.execute('''
            SELECT es.id, es.employee_id, es.shift_id, es.date, es.request_status,
                   e.first_name || ' ' || e.last_name AS employee_name, 
                   s.name AS shift_name
            FROM employee_shift es
            JOIN employees e ON es.employee_id = e.id
            JOIN shifts s ON es.shift_id = s.id
            WHERE es.request_status = 'REQUESTED'
        ''').fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching requests: {e}")
        return []
    finally:
        db.close()
        
def update_request_status(id, request_status):
    db = get_db()
    try:
        db.execute('UPDATE employee_shift SET request_status = ? WHERE id = ?', (request_status, id))
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
        return update_request_status(id, "APPROVED")
    except Exception as e:
        db.rollback()
        print(f"Error approving request: {e}")
        return False
    finally:
        db.close()
        
def reject_request(id):
    db = get_db()
    try:
        return update_request_status(id, "REJECTED")
    except Exception as e:
        db.rollback()
        print(f"Error rejecting request: {e}")
        return False
    finally:
        db.close()