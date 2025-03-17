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




def assign_shift(employee_id, shift_id, date, start_time, end_time, shift_type="Regular", custom_details=None):
    db = get_db()
    
    # ✅ Print received values before inserting into DB
    print(f"DEBUG: Assigning Shift -> Employee: {employee_id}, Shift: {shift_id}, Date: {date}, Start: {start_time}, End: {end_time}")

    try:
        # ✅ Ensure time is correctly formatted
        def format_time(time_str):
            if time_str:
                try:
                    return datetime.strptime(time_str.strip(), '%H:%M').strftime('%H:%M')  # Format HH:MM
                except ValueError:
                    print(f"⚠️ Invalid time format received: {time_str}")
                    return None
            return None

        start_time = format_time(start_time)
        end_time = format_time(end_time)

        print(f"✅ FORMATTED: Start Time: {start_time}, End Time: {end_time}")

        existing = db.execute(
            'SELECT id FROM employee_shift WHERE employee_id = ? AND date = ?',
            (employee_id, date)
        ).fetchone()

        if existing:
            print(f"🔄 Updating existing shift ID {existing['id']}")
            update_employee_shift(existing['id'], employee_id, shift_id, date, start_time, end_time, shift_type, custom_details)
            return existing['id']
        else:
            print(f"🆕 Inserting new shift -> Start: {start_time}, End: {end_time}")

            approval_status = "Pending" if shift_type == "Time Off" else "Approved"

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
        print(f"❌ ERROR assigning shift: {e}")
        return None
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
    print(f"Updating employee_shift {employee_shift_info}")

    try:
        shift = db.execute('SELECT start_time, end_time FROM shifts WHERE id = ?', (shift_id,)).fetchone()

        start_time = datetime.strptime(shift['start_time'], '%I %p').strftime('%H:%M') if shift['start_time'] else None
        end_time = datetime.strptime(shift['end_time'], '%I %p').strftime('%H:%M') if shift['end_time'] else None

        # Determine approval status based on shift type
        approval_status = "Pending" if shift_type == "Time Off" else "Approved"

        db.execute(
            '''
            UPDATE employee_shifts 
            SET employee_id = ?, shift_id = ?, date = ?, request_status = 'NONE', 
                start_time = ?, end_time = ?, shift_type = ?, custom_details = ?, approval_status = ?
            WHERE id = ?
        ''', (employee_id, shift_id, date, start_time, end_time, shift_type, custom_details, approval_status, id))
        
        employee_shift_info = get_detailed_employee_shift(id)
        print(f"Updated employee_shift {employee_shift_info}")

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating employee shift: {e}")
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