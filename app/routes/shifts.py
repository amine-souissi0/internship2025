# app/routes/shifts.py

"""
Shift Management Routes

This module handles the management of shifts, providing routes for:
- / (index): List all shifts
- /add_shift: Add a new shift
- /delete_shift/<id>: Remove a shift
- /edit_shift/<id>: Modify an existing shift
- /toggle_active_shift/<id>: Toggle a shift's active status
"""

from flask import Blueprint, flash,  render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.services import shift_service

shifts_bp = Blueprint('shifts', __name__)

def get_shift_data():
    shifts = shift_service.get_all_shifts()
    existing_shift_names = {shift.name.lower() for shift in shifts}
    available_shift_names = [name for name in ['Morning', 'Evening', 'Night', 'MTA', 'REST', 'Off'] 
                             if name.lower() not in existing_shift_names]
    return shifts, available_shift_names

@shifts_bp.route('/')
@login_required
def index():
    shifts, available_shift_names = get_shift_data()
    return render_template('shifts/shifts.html',
                           shifts=shifts,
                           available_shift_names=available_shift_names,
                           active='shifts')


@shifts_bp.route('/add_shift', methods=['GET','POST'])
def add_shift():
    if request.method == 'POST':
        name = request.form['name']
        print("name post: ", name)
        if name == 'Custom':
            name = request.form['custom_name']
            print("custom_name: ", name)
            
        bg_color = request.form['bg_color']
        text_color = request.form['text_color']
        
        if name.lower() in ['morning', 'evening', 'night']:
            start_hour = request.form['start_hour']
            start_period = request.form['start_period']
            start_time = f"{start_hour} {start_period}"

            end_hour = request.form['end_hour']
            end_period = request.form['end_period']
            end_time = f"{end_hour} {end_period}"

        
            if name and bg_color and text_color and start_time and end_time:
                shift_service.add_shift(name, bg_color, text_color, start_time, end_time)
            else:
                flash('All fields are required.', 'error')
        
        else:
            if name and bg_color and text_color:
                shift_service.add_shift(name, bg_color, text_color)
            else:
                flash('Shift name, background and text color are required.', 'error')

        return redirect(url_for('shifts.index'))
    
    print("selected_shift_name: ", request.args.get('shift_name'))
    shifts, available_shift_names = get_shift_data()
    print("available_shift_names: ", available_shift_names)
    return render_template('shifts/shifts.html',
                           shifts=shifts,
                           available_shift_names=available_shift_names,
                           active='shifts')


@shifts_bp.route('/delete_shift/<int:id>')
def delete_shift(id):
    shift_service.delete_shift(id)
    return redirect(url_for('shifts.index'))


@shifts_bp.route('/edit_shift/<int:id>', methods=['GET', 'POST'])
def edit_shift(id):
    current_shift = next(
        (s for s in shift_service.get_all_shifts() if s.id == id), None)
    if request.method == 'POST':
        name = request.form['shift_name']
        bg_color = request.form['bg_color']
        text_color = request.form['text_color']

        if name.lower() in ['morning', 'evening', 'night']:
            start_hour = request.form['start_hour']
            start_period = request.form['start_period']
            end_hour = request.form['end_hour']
            end_period = request.form['end_period']
            start_time = f"{start_hour} {start_period}"
            end_time = f"{end_hour} {end_period}"
        else:
            start_time = None
            end_time = None

        shift_service.update_shift(id, name, bg_color, text_color, start_time, end_time)

        return redirect(url_for('shifts.index'))
    return render_template('shifts/edit_shift.html', shift=current_shift)


@shifts_bp.route('/toggle_active_shift/<int:id>', methods=['POST'])
@login_required
def toggle_active_shift(id):
    shift_service.toggle_active_shift(id)
    return redirect(url_for('shifts.index'))


