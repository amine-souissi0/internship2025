# app/routes/board.py

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from collections import defaultdict
from app.services import employee_shift_service, employee_service

board_bp = Blueprint('board', __name__)

@board_bp.route('/')
@login_required
def index():
    today = datetime.now().date()
    week_offset = int(request.args.get('week_offset', 0))
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)

    dates = [start_of_week + timedelta(days=i) for i in range(7)]
    formatted_dates = [d.strftime("%Y-%m-%d") for d in dates]

    employee_shifts_data = employee_shift_service.get_all_employee_shifts()
    employees = employee_service.get_all_employees()
    all_shifts = employee_shift_service.get_all_shifts()  # Fetch all available shifts

    # Debug output
    print("\n=== DEBUG: FETCHED EMPLOYEES ===")
    for emp in employees:
        print(f"Employee ID: {emp.id}, Name: {emp.fullname}, Team: {emp.team}")

    print("\n=== DEBUG: RAW SHIFT DATA ===")
    print(employee_shifts_data)

    # Initialize shift mapping
    shifts_by_employee = defaultdict(dict)

    if isinstance(employee_shifts_data, dict) and 'shifts_by_team' in employee_shifts_data:
        for team_name, shifts_list in employee_shifts_data['shifts_by_team'].items():
            for emp_shift in shifts_list:
                employee_name = emp_shift.get('employee_name', '')
                shift_date = emp_shift.get('employee_shift', {}).get('date')

                matching_employee = next((emp for emp in employees if emp.fullname == employee_name), None)
                if not matching_employee:
                    print(f"⚠️ WARNING: No matching employee found for {employee_name}")
                    continue

                employee_id = matching_employee.id
                if shift_date in formatted_dates:
                    shift_name = emp_shift.get('shift_name', 'No Shift')
                    start_time = emp_shift['employee_shift'].get('start_time', '-')
                    end_time = emp_shift['employee_shift'].get('end_time', '-')
                    approval_status = emp_shift['employee_shift'].get('approval_status', 'Approved')
                    # Only include shifts that are not "Rejected"
                    if approval_status != 'Rejected':
                        shifts_by_employee[employee_id][shift_date] = {
                            'display': f"{shift_name} ({start_time} - {end_time})",
                            'approval_status': approval_status
                        }

    print("\n=== DEBUG: FINAL SHIFT MAPPING ===")
    for emp_id, shifts in shifts_by_employee.items():
        print(f"Employee {emp_id}: {shifts}")

    teams = defaultdict(list)
    for employee in employees:
        team_name = getattr(employee, 'team', "No Team")
        teams[team_name].append(employee)

    return render_template(
        'board/board.html',
        dates=dates,
        teams=teams,
        shifts_by_employee=shifts_by_employee,
        week_offset=week_offset,
        employees=employees,
        all_shifts=all_shifts  # Pass all shifts to the template
    )

@board_bp.route('/select_week', methods=['POST'])
def select_week():
    selected_date = datetime.strptime(request.form['selected_date'], '%Y-%m-%d')
    current_date = datetime.now()
    week_offset = (selected_date.isocalendar()[1] - current_date.isocalendar()[1])
    return redirect(url_for('board.index', week_offset=week_offset))

@board_bp.route('/update_shifts', methods=['POST'])
@login_required
def update_shifts():
    try:
        all_shifts = employee_shift_service.get_all_shifts()
        shift_id_to_name = {str(shift['id']): shift['name'].upper() for shift in all_shifts}
        
        # Get all existing shifts to compare with submitted data
        submitted_data = request.form
        processed_employee_dates = set()

        for key, value in submitted_data.items():
            if key.startswith('shift_'):
                _, employee_id, date = key.split('_')
                submitted_shift_id = value if value else None

                # Track which employee-date pairs are being processed to avoid duplicates
                employee_date_key = f"{employee_id}_{date}"
                if employee_date_key in processed_employee_dates:
                    continue
                processed_employee_dates.add(employee_date_key)

                # Get the existing shift for this employee and date
                existing_shift = employee_shift_service.get_existing_shift(employee_id, date)
                
                # Fetch the existing shift_id from the database (if it exists)
                existing_shift_id = None
                if existing_shift:
                    existing_shift_row = employee_shift_service.get_existing_shift_row(employee_id, date)
                    existing_shift_id = str(existing_shift_row['shift_id']) if existing_shift_row else None

                # Only update if the submitted shift_id is different from the existing one
                if submitted_shift_id != existing_shift_id:
                    # Delete the existing shift for this employee and date
                    employee_shift_service.delete_assignment_by_employee_and_date(employee_id, date)

                    if submitted_shift_id:
                        # Assign a new shift if a shift_id is provided
                        shift = next((s for s in all_shifts if str(s['id']) == submitted_shift_id), None)
                        if shift:
                            # Determine the shift_type and approval_status based on the shift name
                            shift_name = shift['name'].upper()
                            if shift_name in ['REST', 'OFF']:
                                shift_type = shift_name
                                approval_status = 'Pending'  # New REST and OFF shifts start as Pending
                            else:
                                shift_type = "Regular"
                                approval_status = "Approved"

                            employee_shift_service.assign_shift_with_status(
                                employee_id=employee_id,
                                shift_id=submitted_shift_id,
                                date=date,
                                start_time=shift['start_time'],
                                end_time=shift['end_time'],
                                shift_type=shift_type,
                                approval_status=approval_status
                            )

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating shifts: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500