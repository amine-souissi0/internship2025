# app/services/employee_shift_service.py

"""
Employee Shift Service

This module provides functions for managing employee shifts:
- get_all_employee_shifts: Retrieve all employee shifts
- assign_shift: Assign a shift to an employee
- delete_assignment: Remove a shift assignment
- get_employee_shift: Get a specific employee shift
- update_employee_shift: Update an employee shift
- format_time: Helper function to format time
"""

from app import get_db
from app.models.employee_shift import EmployeeShift
from datetime import datetime
from app.utils.time_utils import sum_overtime, format_time
from app.utils.debug import get_detailed_employee_shift



def add_employee_shift(employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employee_shift (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status))
    conn.commit()
    conn.close()



def get_all_employee_shifts():
    db = get_db()
    try:
        rows = db.execute('''
            SELECT es.id, es.employee_id, es.shift_id, es.date, 
                   e.first_name || ' ' || e.last_name AS employee_name, 
                   s.name AS shift_name, 
                   es.start_time, es.end_time, es.shift_type, es.custom_details, es.approval_status
            FROM employee_shift es
            LEFT JOIN employees e ON es.employee_id = e.id
            LEFT JOIN shifts s ON es.shift_id = s.id
            ORDER BY e.first_name
        ''').fetchall()

        shifts_by_team = {}

        for row in rows:
            shift_info = {
                'employee_shift': {
                    'id': row['id'],
                    'date': row['date'],
                    'start_time': row['start_time'] if row['start_time'] and row['start_time'] != "00:00" else None,
                    'end_time': row['end_time'] if row['end_time'] and row['end_time'] != "00:00" else None,
                    'shift_type': row['shift_type'],
                    'custom_details': row['custom_details'],
                    'approval_status': row['approval_status'],
                },
                'employee_name': row['employee_name'],
                'shift_name': row['shift_name']
            }

            team_name = row['employee_name'] or 'No Team'
            if team_name not in shifts_by_team:
                shifts_by_team[team_name] = []
            shifts_by_team[team_name].append(shift_info)

        return {'shifts_by_team': shifts_by_team}
    except Exception as e:
        print(f"Error fetching employee shifts: {e}")
        return {'shifts_by_team': {}}
    finally:
        db.close()




# app/services/employee_shift_service.py

# app/services/employee_shift_service.py

def assign_shift(employee_id, shift_id, date, start_time, end_time, shift_type="Regular", custom_details=None, approval_status="Approved"):
    db = get_db()
    try:
        # Check if there's an existing shift for this employee and date
        existing_shift = db.execute(
            'SELECT id FROM employee_shift WHERE employee_id = ? AND date = ?',
            (employee_id, date)
        ).fetchone()
        if existing_shift:
            db.execute('DELETE FROM employee_shift WHERE id = ?', (existing_shift['id'],))

        # Insert new shift assignment with all fields
        db.execute(
            '''
            INSERT INTO employee_shift (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status)
        )
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error assigning shift: {e}")
        return False
    finally:
        db.close()




def delete_assignment(id):
    db = get_db()
    employee_shift_info = get_detailed_employee_shift(id)
    print(f"Deleting assignment {employee_shift_info}")
    try:
        db.execute('DELETE FROM employee_shift WHERE id = ?', (id, ))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting assignment: {e}")
        return False
    finally:
        db.close()


def get_employee_shift(id):
    print(f"get_employee_shift id: {id}")
    db = get_db()
    try:
        row = db.execute(
            '''
            SELECT es.id, es.employee_id, es.shift_id, es.date, 
                es.actual_start_time, es.actual_end_time, es.overtime_hours,
                   e.first_name || ' ' || e.last_name AS employee_name, 
                   s.name AS shift_name, s.start_time, s.end_time
            FROM employee_shift es
            JOIN employees e ON es.employee_id = e.id
            JOIN shifts s ON es.shift_id = s.id
            WHERE es.id = ?
        ''', (id, )).fetchone()
        if row:
            return {
            'employee_shift':EmployeeShift(row['id'], row['employee_id'],
                                 row['shift_id'], row['date'],
                                 format_time(row['actual_start_time']),
                                 format_time(row['actual_end_time']),
                                 row['overtime_hours']),
            'shift_name':row['shift_name'],
            'shift_start_time':row['start_time'],
            'shift_end_time':row['end_time']
            }
        return None
    except Exception as e:
        print(f"Error fetching employee shift: {e}")
        return None
    finally:
        db.close()


def update_employee_shift(id, employee_id, shift_id, date, shift_type="Regular", custom_details=None):
    db = get_db()
    employee_shift_info = get_detailed_employee_shift(id)
    try:
        shift = db.execute('SELECT name, start_time, end_time FROM shifts WHERE id = ?', (shift_id,)).fetchone()

        start_time = datetime.strptime(shift['start_time'], '%I %p').strftime('%H:%M') if shift['start_time'] else None
        end_time = datetime.strptime(shift['end_time'], '%I %p').strftime('%H:%M') if shift['end_time'] else None

        shift_name = shift['name'].upper() if shift else ""
        
        if shift_name == "OFF":
            shift_type = "OFF"
            approval_status = "Approved"
        elif shift_name == "REST":
            shift_type = "REST"
            approval_status = "Pending"
        else:
            shift_type = "Regular"
            approval_status = "Approved"

        # Update clearly
        db.execute(
            '''
            UPDATE employee_shift 
            SET employee_id = ?, shift_id = ?, date = ?, 
                start_time = ?, end_time = ?, shift_type = ?, 
                custom_details = ?, approval_status = ?
            WHERE id = ?
            ''',
            (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status, id)
        )

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating shift: {e}")
        return False
    finally:
        db.close()

        
def delete_assignment_by_employee_and_date(employee_id, date):
    db = get_db()
    try:
        existing = db.execute(
            'SELECT id FROM employee_shift WHERE employee_id = ? AND date = ?',
            (employee_id, date)
        ).fetchone()

        if existing:
            delete_assignment(existing['id'])
        else:
            print(f"No employee shift found with employee_id {employee_id} and date {date}")
        db.execute('DELETE FROM employee_shift WHERE employee_id = ? AND date = ?', (employee_id, date))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting assignment: {e}")
        return False
    finally:
        db.close()


def get_all_shifts():
    db = get_db()
    try:
        shifts = db.execute('SELECT * FROM shifts').fetchall()  # Retrieve all shifts from the database
        return shifts
    except Exception as e:
        print(f"Error fetching shifts: {e}")
        return []
    finally:
        db.close()


def get_existing_shift(employee_id, date):
    db = get_db()
    try:
        row = db.execute(
            '''
            SELECT shift_type, approval_status 
            FROM employee_shift 
            WHERE employee_id = ? AND date = ?
            ''', (employee_id, date)).fetchone()
        return row if row else None
    except Exception as e:
        print(f"Error getting existing shift: {e}")
        return None
    finally:
        db.close()

def assign_shift_with_status(employee_id, shift_id, date, start_time, end_time, shift_type="Regular", custom_details=None, approval_status="Approved"):
    db = get_db()
    
    print(f"DEBUG: Assigning Shift with Status -> Employee: {employee_id}, Shift: {shift_id}, Date: {date}, Start: {start_time}, End: {end_time}, Shift Type: {shift_type}, Status: {approval_status}")

    try:
        # Format time
        def format_time(time_str):
            if time_str:
                try:
                    return datetime.strptime(time_str.strip(), '%H:%M').strftime('%H:%M')
                except ValueError:
                    print(f"⚠️ Invalid time format received: {time_str}")
                    return None
            return None

        start_time = format_time(start_time)
        end_time = format_time(end_time)

        print(f"✅ FORMATTED: Start Time: {start_time}, End Time: {end_time}")

        result = db.execute(
            '''
            INSERT INTO employee_shift (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status)
        )

        db.commit()
        return result.lastrowid
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR assigning shift with status: {e}")
        return None
    finally:
        db.close()


# app/services/employee_shift_service.py

def get_existing_shift_row(employee_id, date):
    db = get_db()
    try:
        row = db.execute(
            '''
            SELECT id, employee_id, shift_id, date, shift_type, approval_status 
            FROM employee_shift 
            WHERE employee_id = ? AND date = ?
            ''', (employee_id, date)).fetchone()
        return row if row else None
    except Exception as e:
        print(f"Error getting existing shift row: {e}")
        return None
    finally:
        db.close()



def get_approved_off_days(employee_id):
    db = get_db()
    try:
        result = db.execute(
            '''
            SELECT COUNT(*) as approved_off_days
            FROM employee_shift
            WHERE employee_id = ? AND shift_type = 'OFF' AND approval_status = 'Approved'
            ''',
            (employee_id,)
        ).fetchone()
        return result['approved_off_days'] if result else 0
    except Exception as e:
        print(f"Error fetching approved off days: {e}")
        return 0


def approve_off_day_request(request_id):
    db = get_db()
    try:
        shift_request = db.execute(
            'SELECT employee_id, approval_status FROM employee_shift WHERE id = ?',
            (request_id,)
        ).fetchone()

        if shift_request and shift_request['approval_status'] != 'Approved':
            db.execute('''
                UPDATE employee_shift SET approval_status = 'Approved' WHERE id = ?
            ''', (request_id,))

            # Clearly reduce off days only now
            employee_id = shift_request['employee_id']
            user = db.execute('SELECT remaining_off_days FROM users WHERE employee_id = ?', (employee_id,)).fetchone()

            if user and user['remaining_off_days'] > 0:
                db.execute(
                    'UPDATE users SET remaining_off_days = remaining_off_days - 1 WHERE employee_id = ?',
                    (employee_id,)
                )
            else:
                raise Exception("User has no remaining off days.")

            db.commit()
            return True
        else:
            return False

    except Exception as e:
        db.rollback()
        print(f"Error during approval: {e}")
        return False
    finally:
        db.close()































































































































































        
                