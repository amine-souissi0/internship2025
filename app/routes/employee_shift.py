# app/routes/employee_shift.py

"""
Employee Shift Management Routes

This module handles the management of employee shifts, providing routes for:
- / (index): List all employee shifts
- /assign: Create a new shift assignment
- /delete/<id>: Remove a shift assignment
- /edit/<id>: Modify an existing shift assignment
"""

from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.services import employee_shift_service, employee_service, shift_service
from flask_login import login_required, current_user
from app.utils.email_utils import send_email  # (Optional for email notifications)

employee_shift_bp = Blueprint('employee_shift', __name__)





@employee_shift_bp.route('/')
@login_required
def index():
    employee_shifts = employee_shift_service.get_all_employee_shifts()
    employees = employee_service.get_all_employees()
    shifts = shift_service.get_all_active_shifts()

    # ✅ Debugging - Print Employee Shifts Sent to Frontend
    for team, shift_list in employee_shifts['shifts_by_team'].items():
        for shift in shift_list:
            print(f"DEBUG: Employee: {shift['employee_name']}, Date: {shift['employee_shift']['date']}, Start: {shift['employee_shift']['start_time']}, End: {shift['employee_shift']['end_time']}")



    return render_template('employee_shifts/employee_shifts.html',
                           employee_shifts=employee_shifts,
                           employees=employees,
                           shifts=shifts,
                           active='employee_shifts')




# app/routes/employee_shift.py

# app/routes/employee_shift.py

@employee_shift_bp.route('/assign', methods=['POST'])
def assign_shift():
    employee_id = request.form['employee_id']
    shift_id = request.form['shift_id']
    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    shift_type = request.form.get('shift_type', 'Regular')
    custom_details = request.form.get('custom_details', None)

    if employee_id and shift_id and date and start_time and end_time:
        try:
            # Check if a shift already exists for this employee on this date
            existing_shift = employee_shift_service.get_existing_shift(employee_id, date)
            if existing_shift:
                flash(f'Cannot assign shift: Employee already has a shift on {date}.', 'error')
                return redirect(url_for('employee_shift.index'))
            # Fetch the shift name to determine approval status
            shift = shift_service.get_shift_by_id(shift_id)
            shift_name = shift.name.upper() if shift else ""
            approval_status = 'Pending' if 'OFF' in shift_name or shift_type == 'Time Off' else 'Approved'

            employee_shift_service.assign_shift(
                employee_id=employee_id,
                shift_id=shift_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                shift_type=shift_type,
                custom_details=custom_details,
                approval_status=approval_status
            )
            flash('Shift assigned successfully!', 'success')
        except ValueError as ve:
            flash(str(ve), 'error')  # Flash the conflict message
        except Exception as e:
            flash(f'An error occurred while assigning the shift: {str(e)}', 'error')
    else:
        flash('Please fill in all required fields.', 'error')

    return redirect(url_for('employee_shift.index'))




@employee_shift_bp.route('/delete/<int:id>')
def delete_assignment(id):
    employee_shift_service.delete_assignment(id)

    return redirect(url_for('employee_shift.index'))


@employee_shift_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_assignment(id):
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        shift_id = request.form['shift_id']
        date = request.form['date']

        if employee_shift_service.update_employee_shift(
                id, employee_id, shift_id, date):
            flash('Shift updated successfully', 'success')
        else:
            flash('Failed to update employee shift', 'error')

    employee_shift = employee_shift_service.get_employee_shift(id)
    employees = employee_service.get_all_employees()
    shifts = shift_service.get_all_shifts()

    return render_template('employee_shifts/edit_employee_shift.html',
                           employee_shift=employee_shift,
                           employees=employees,
                           shifts=shifts)



# Approve Time Off Request
@employee_shift_bp.route('/approve_request/<int:id>', methods=['POST'])
@login_required
def approve_request(id):
    success = employee_shift_service.update_approval_status(id, "Approved")
    
    if success:
        flash("Time Off request approved successfully!", "success")

        # OPTIONAL: Send email notification to employee
        shift_data = employee_shift_service.get_employee_shift(id)
        if shift_data and shift_data.get('employee_shift'):
            employee_email = employee_shift_service.get_employee_email(shift_data['employee_shift'].employee_id)
            send_email(employee_email, "Time Off Approved", f"Your Time Off request for {shift_data['employee_shift'].date} has been approved.")
    
    else:
        flash("Failed to approve request. Please try again.", "danger")

    return redirect(url_for('employee_shift.index'))


# Reject Time Off Request
@employee_shift_bp.route('/reject_request/<int:id>', methods=['POST'])
@login_required
def reject_request(id):
    success = employee_shift_service.update_approval_status(id, "Rejected")
    
    if success:
        flash("Time Off request rejected.", "warning")

        # OPTIONAL: Send email notification to employee
        shift_data = employee_shift_service.get_employee_shift(id)
        if shift_data and shift_data.get('employee_shift'):
            employee_email = employee_shift_service.get_employee_email(shift_data['employee_shift'].employee_id)
            send_email(employee_email, "Time Off Rejected", f"Your Time Off request for {shift_data['employee_shift'].date} has been rejected.")
    
    else:
        flash("Failed to reject request. Please try again.", "danger")

    return redirect(url_for('employee_shift.index'))


