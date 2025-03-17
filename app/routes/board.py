from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from datetime import datetime, timedelta
from collections import defaultdict
from app.services import employee_shift_service, shift_service, employee_service

board_bp = Blueprint('board', __name__)

@board_bp.route('/')
@login_required
def index():
    # ✅ Get the current date and calculate the start of the week
    today = datetime.now().date()
    week_offset = int(request.args.get('week_offset', 0))
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)

    # ✅ Generate dates for the current week
    dates = [start_of_week + timedelta(days=i) for i in range(7)]
    formatted_dates = [d.strftime("%Y-%m-%d") for d in dates]

    # ✅ Fetch required data
    employee_shifts_data = employee_shift_service.get_all_employee_shifts()
    employees = employee_service.get_all_employees()
    shifts = shift_service.get_all_active_shifts()

    # ✅ Organize shifts by employee and date
    shifts_by_employee = defaultdict(lambda: defaultdict(str))

    for team, shifts_list in employee_shifts_data.get('shifts_by_team', {}).items():
        for emp_shift in shifts_list:
            employee_id = emp_shift['employee_shift'].get('employee_id')
            shift_date = emp_shift['employee_shift'].get('date')

            if employee_id and shift_date:
                formatted_date = shift_date  # Already in "YYYY-MM-DD" format

                if formatted_date in formatted_dates:  # ✅ Only keep shifts within the displayed week
                    shift_name = emp_shift.get('shift_name', 'No Shift')
                    start_time = emp_shift['employee_shift'].get('start_time', '-')
                    end_time = emp_shift['employee_shift'].get('end_time', '-')

                    shifts_by_employee[int(employee_id)][formatted_date] = f"{shift_name} ({start_time} - {end_time})"

    # ✅ Debugging: Print shift assignments
    print("\n=== DEBUG: SHIFT ASSIGNMENTS ===")
    for emp_id, shifts in shifts_by_employee.items():
        print(f"Employee {emp_id}: {shifts}")

    # ✅ Group employees by team
    teams = defaultdict(list)
    for employee in employees:
        team_name = getattr(employee, 'team', "No Team")
        teams[team_name].append(employee)

    # ✅ Render the board template
    return render_template(
        'board/board.html',
        dates=dates,
        teams=teams,
        shifts_by_employee=shifts_by_employee,
        week_offset=week_offset,
        employees=employees,
        active='board'
    )

@board_bp.route('/assign_shift', methods=['POST'])
@login_required
def assign_shift():
    employee_id = request.form.get('employee_id')
    date = request.form.get('date')
    shift_id = request.form.get('shift_id')
    week_offset = request.form.get('week_offset', 0)

    if employee_id and date:
        if shift_id:
            employee_shift_service.assign_shift(employee_id, shift_id, date)
        else:
            employee_shift_service.delete_assignment_by_employee_and_date(employee_id, date)

    return redirect(url_for('board.index', week_offset=week_offset))

@board_bp.route('/select_week', methods=['POST'])
def select_week():
    selected_date = datetime.strptime(request.form['selected_date'], '%Y-%m-%d')
    current_date = datetime.now()
    week_offset = (selected_date.isocalendar()[1] - current_date.isocalendar()[1])
    return redirect(url_for('board.index', week_offset=week_offset))
