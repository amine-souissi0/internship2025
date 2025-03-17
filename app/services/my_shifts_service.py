# app/services/my_shifts_service.py

"""
My Shifts Service

This module provides functions for managing an employee's own shifts:
- get_employee_shifts_by_employee_id: Get shifts for a specific employee
- update_actual_times: Update actual start and end times for a shift
- update_total_overtime: Calculate total overtime of the current user
"""


from app.database.db import get_db
from app.models.employee_shift import EmployeeShift
from datetime import datetime, timedelta
from app.utils.time_utils import *


def get_employee_shifts_by_employee_id(employee_id):
    db = get_db()
    try:
        rows = db.execute(
            '''
            SELECT es.id, es.employee_id, es.shift_id, es.date, 
                es.actual_start_time, es.actual_end_time, es.overtime_hours, es.request_status,
                   e.first_name || ' ' || e.last_name AS employee_name, 
                   s.name AS shift_name, s.bg_color AS shift_bg_color, s.text_color AS shift_text_color
            FROM employee_shift es
            JOIN employees e ON es.employee_id = e.id
            JOIN shifts s ON es.shift_id = s.id
            WHERE es.employee_id = ?
        ''', (employee_id, )).fetchall()
        shifts = [{
            'employee_shift': 
                EmployeeShift(row['id'], row['employee_id'], 
                    row['shift_id'], row['date'], 
                    format_time(row['actual_start_time']),
                    format_time(row['actual_end_time']),
                    row['overtime_hours'],
                    row['request_status']),
            'employee_name':row['employee_name'],
            'shift_name':row['shift_name'],
            'shift_bg_color': row['shift_bg_color'],
            'shift_text_color': row['shift_text_color']            
        } for row in rows]
        total_overtime = sum_overtime(row['overtime_hours'] for row in rows)
        return {
            'shifts': shifts,
            'total_overtime': total_overtime
        }
    except Exception as e:
        print(f"Error fetching employee shifts: {e}")
        return []
    finally:
        db.close()


def update_actual_times(id, actual_start_time, actual_end_time):
    
    print(f"update_actual_times: start {actual_start_time}, end {actual_end_time}")

    db = get_db()
    try:
        shift_details = db.execute(
            '''
            SELECT es.employee_id, es.actual_start_time, es.actual_end_time, s.start_time, s.end_time 
            FROM employee_shift es
            JOIN shifts s ON es.shift_id = s.id
            WHERE es.id = ?
        ''', (id, )).fetchone()

        query = 'UPDATE employee_shift SET '
        params = []

        # Process actual start time and end time
        actual_start_time = actual_start_time or shift_details['actual_start_time']
        actual_end_time = actual_end_time or shift_details['actual_end_time']
        
        print(f"actual_start_time: {actual_start_time}, actual_end_time {actual_end_time}")
        
        # Parse times
        actual_start = parse_time(actual_start_time)
        actual_end = parse_time(actual_end_time)
        shift_start = parse_time(shift_details['start_time'], '%I %p')
        shift_end = parse_time(shift_details['end_time'], '%I %p')

        # Calculate overtime
        if actual_start_time and actual_end_time and shift_start and shift_end:
            overtime_minutes = calculate_overtime_minutes(
                actual_start, actual_end, 
                shift_start, shift_end
            )
            overtime_str = minutes_to_hhmm(overtime_minutes)
        else:
            overtime_str = '00:00'
        print(f"overtime_hours: {overtime_str}")
        
        query = 'UPDATE employee_shift SET actual_start_time = ?, actual_end_time = ?, overtime_hours = ? WHERE id = ?'
        params = (actual_start_time, actual_end_time, overtime_str, id)

        print(f"query:  {query}, with params {params}")
        
        db.execute(query, params)
        db.commit()
                
        update_total_overtime(shift_details['employee_id'])
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating actual times: {e}")
        return False
    finally:
        db.close()

        
def update_total_overtime(employee_id):
    print(f"total overtime update with id: {employee_id}")
    db = get_db()
    try:
        # Calculate total overtime as a sum of all employee's shifts
        rows = db.execute('''
            SELECT overtime_hours
            FROM employee_shift
            WHERE employee_id = ?
        ''', (employee_id,)).fetchall()

        # Calculate total overtime using existing sum_overtime function
        total_overtime = sum_overtime(row['overtime_hours'] for row in rows)
        
        # Update employee's total overtime
        query = 'UPDATE employees SET total_overtime = ? WHERE id = ?'
        params = (total_overtime, employee_id)

        print(f"query:  {query}, with params {params}")
        db.execute(query, params)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating total overtime: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()