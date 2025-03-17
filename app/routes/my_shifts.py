# app/routes/my_shifts.py

"""
My Shifts Management Routes

This module handles the management of an employee's own shifts, providing routes for:
- / (index): List all shifts for the current employee
- /assign: Assign a new shift to the current employee
- /delete/<id>: Remove a shift assignment
- /edit/<id>: Modify an existing shift assignment
- /update_actual_times/<id>: Update actual start and end times for a shift
"""

from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.services import employee_shift_service, employee_service, shift_service, my_shifts_service
from dateutil.relativedelta import relativedelta

from app.utils.time_utils import get_month_dates, calculate_month_offset, get_month_calendar
from datetime import datetime

my_shifts_bp = Blueprint('my_shifts', __name__)


@my_shifts_bp.route('/')
@login_required
def index():
    employee_id = current_user.employee_id
    shifts = shift_service.get_all_active_shifts()
    employee = employee_service.get_employee_by_id(employee_id)
    
    if not employee:
        flash(
            "Your account is not associated with an employee. Please contact the administrator.",
            "warning")
        employee_shifts = {'shifts': [], 'total_overtime': '00:00'}
    else:
        employee_shifts = my_shifts_service.get_employee_shifts_by_employee_id(employee_id)

    month_offset = int(request.args.get('month_offset', 0))
    target_date = datetime.now().date() + relativedelta(months=month_offset)
    calendar_weeks = get_month_calendar(target_date.year, target_date.month)
    
    # Organize shifts by date
    shifts_by_date = {}
    for emp_shift in employee_shifts['shifts']:
        shift_date = emp_shift['employee_shift'].date
        shifts_by_date[shift_date] = {
            'name': emp_shift['shift_name'],
            'bg_color': emp_shift['shift_bg_color'],
            'text_color': emp_shift['shift_text_color'],
            'request_status': emp_shift['employee_shift'].get_display_status(emp_shift['shift_name'])
        }

    return render_template('my_shifts/my_shifts.html',
                           employee_shifts=employee_shifts,
                           employee=employee,
                           shifts=shifts,
                           calendar_weeks=calendar_weeks,
                           target_date=target_date,
                           shifts_by_date=shifts_by_date,
                           month_offset=month_offset,
                           active='my_shifts',
                           username=current_user.username)


@my_shifts_bp.route('/assign', methods=['POST'])
def assign_shift():
    employee_id = request.form['employee_id']
    shift_id = request.form['shift_id']
    date = request.form['date']
    month_offset = request.form.get('month_offset', 0)

    if employee_id and date:
        if shift_id:
            employee_shift_service.assign_shift(employee_id, shift_id, date)
        else:
            employee_shift_service.delete_assignment_by_employee_and_date(employee_id, date)

    return redirect(url_for('my_shifts.index', month_offset=month_offset, employee_id=employee_id))


@my_shifts_bp.route('/delete/<int:id>')
def delete_assignment(id):
    employee_id = request.args.get('employee_id')
    employee_shift_service.delete_assignment(id)

    return redirect(url_for('my_shifts.index', employee_id=employee_id))


@my_shifts_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_assignment(id):
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        shift_id = request.form['shift_id']
        date = request.form['date']

        if employee_shift_service.update_employee_shift(
                id, employee_id, shift_id, date):
            return redirect(url_for('my_shifts.index',
                                    employee_id=employee_id))
        else:
            flash('Failed to update my shift', 'error')

    employee_shift = employee_shift_service.get_employee_shift(id)
    employees = employee_service.get_all_employees()
    shifts = shift_service.get_all_shifts()

    return render_template('my_shifts/edit_my_shift.html',
                           employee_shift=employee_shift,
                           employees=employees,
                           shifts=shifts)


@my_shifts_bp.route('/update_actual_times/<int:id>', methods=['GET', 'POST'])
def update_actual_times(id):
    employee_shift_data = employee_shift_service.get_employee_shift(id)
    shift_start_time = employee_shift_data['shift_start_time']
    shift_end_time = employee_shift_data['shift_end_time']
    
    if employee_shift_data['employee_shift'].actual_start_time:
        actual_start_time = datetime.strptime(employee_shift_data['employee_shift'].actual_start_time, '%I:%M %p').strftime('%H:%M')
    elif shift_start_time:
        actual_start_time = datetime.strptime(shift_start_time, '%I %p').strftime('%H:%M')
    else:
        actual_start_time = shift_start_time
    if employee_shift_data['employee_shift'].actual_end_time:
        actual_end_time = datetime.strptime(employee_shift_data['employee_shift'].actual_end_time, '%I:%M %p').strftime('%H:%M')
    elif shift_end_time:
        actual_end_time = datetime.strptime(shift_end_time, '%I %p').strftime('%H:%M')
    else:
        actual_end_time = shift_end_time

    if employee_shift_data is None:
        flash('Employee shift not found', 'error')
        return redirect(url_for('my_shifts.index'))

    if request.method == 'POST':
        actual_start_time = request.form['actual_start_time']
        actual_end_time = request.form['actual_end_time']
        employee_id = request.form.get('employee_id')

        # Update the database with actual times
        if my_shifts_service.update_actual_times(id, actual_start_time,
                                                 actual_end_time):
            flash('Actual times updated successfully', 'success')
        else:
            flash('Failed to update actual times', 'error')

        return redirect(url_for('my_shifts.index', employee_id=employee_id))

    employee_id = request.args.get(
        'employee_id') or employee_shift_data['employee_shift'].employee_id
    
    print(f"shift_start_time {shift_start_time}")
    print(f"shift_end_time {shift_end_time}")
    print(f"actual_start_time {actual_start_time}")
    print(f"actual_end_time {actual_end_time}")

    return render_template(
        'my_shifts/edit_times.html',
        shift_name=employee_shift_data['shift_name'],
        employee_shift=employee_shift_data['employee_shift'],
        employee_id=employee_id,
        shift_start_time=shift_start_time,
        shift_end_time=shift_end_time,
        actual_start_time=actual_start_time,
        actual_end_time=actual_end_time
        )

    
@my_shifts_bp.route('/select_month', methods=['POST'])
def select_month():
    selected_date = datetime.strptime(request.form['selected_date'], '%Y-%m-%d')
    current_date = datetime.now()
    month_offset = (selected_date.isocalendar()[1] - current_date.isocalendar()[1])
    return redirect(url_for('my_shifts.index', month_offset=month_offset))