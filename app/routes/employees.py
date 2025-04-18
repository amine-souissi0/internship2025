# app/routes/employees.py

"""
Employee Management Routes

This module handles the management of employees, providing routes for:
- / (index): List all employees
- /add: Add a new employee
- /delete/<id>: Remove an employee
- /edit/<id>: Modify an existing employee's details
- /reveal_password/<id>: Display an employee's password
- /edit_password/<id>: Change an employee's password
- /update_role/<id>: Update an employee's role
"""

from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.services import employee_service
from app.services.user_service import create_user, get_user_by_id
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash

employees_bp = Blueprint('employees', __name__)

# Helper function to check if the current user is a manager
def is_manager():
    return current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role == 'manager'

@employees_bp.route('/')
@login_required
def index():
    employees_with_users = employee_service.get_all_employees_with_users()
    for emp in employees_with_users:
        print(f"Employee: {emp['employee'].fullname}, User ID: {emp['user_id']}")
    return render_template('employees/employees.html',
                           employees_with_users=employees_with_users,
                           active='employees',
                           is_manager=is_manager())

@employees_bp.route('/add', methods=['POST'])
@login_required
def add_employee():
    if not is_manager():
        flash('Only managers can add employees.', 'error')
        return redirect(url_for('employees.index'))

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    team = request.form['team']
    username = request.form['username']
    password = request.form['password']
    employee_id = employee_service.add_employee(first_name, last_name, team)
    
    if employee_id:
        if create_user(username, password, employee_id):
            flash('Employee and user account created successfully', 'success')
        else:
            flash('Employee created, but user account creation failed, suppressing employee', 'warning')
            employee_service.delete_employee(employee_id)
    else:
        flash('Failed to create employee', 'error')
    
    return redirect(url_for('employees.index'))

@employees_bp.route('/delete/<int:id>')
@login_required
def delete_employee(id):
    if not is_manager():
        flash('Only managers can delete employees.', 'error')
        return redirect(url_for('employees.index'))
    
    employee_service.delete_employee(id)
    flash('Employee deleted successfully.', 'success')
    return redirect(url_for('employees.index'))

@employees_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    if not is_manager():
        flash('Only managers can edit employee information.', 'error')
        return redirect(url_for('employees.index'))

    employee = next(
        (e for e in employee_service.get_all_employees() if e.id == id), None)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        team = request.form['team']

        employee_service.update_employee(id, first_name, last_name, team)
        flash('Employee updated successfully.', 'success')
        return redirect(url_for('employees.index'))
    return render_template('employees/edit_employee.html', employee=employee)

@employees_bp.route('/reveal_password/<int:id>', methods=['POST'])
@login_required
def reveal_password(id):
    if not is_manager():
        flash('Only managers can reveal passwords.', 'error')
        return redirect(url_for('employees.index'))

    employee_with_user = next((e for e in employee_service.get_all_employees_with_users() if e['user_id'] == id), None)
    if employee_with_user and employee_with_user['password_hash']:
        user = get_user_by_id(employee_with_user['user_id'])
        return render_template('employees/employee_pwd.html', employee=employee_with_user['employee'], password=user.password)
    return redirect(url_for('employees.index'))

@employees_bp.route('/edit_password/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_password(id):
    if not is_manager():
        flash('Only managers can edit passwords.', 'error')
        return redirect(url_for('employees.index'))

    employee_with_user = next((e for e in employee_service.get_all_employees_with_users() if e['employee'].id == id), None)
    if employee_with_user:
        if request.method == 'POST':
            new_password = request.form['new_password']
            user = get_user_by_id(employee_with_user['user_id'])
            user.password = new_password
            print(f"New encrypted password: {user.password_hash}")
            print(f"New encrypted password: {user.password}")
            employee_service.save_new_password(user.password_hash, employee_with_user['user_id'])
            flash('Password updated successfully.', 'success')
            return redirect(url_for('employees.index'))
        return render_template('employees/employee_pwd.html', employee=employee_with_user['employee'], edit_mode=True)
    return redirect(url_for('employees.index'))

@employees_bp.route('/update_role/<int:id>', methods=['POST'])
@login_required
def update_role(id):
    if not is_manager():
        flash('Only managers can update roles.', 'error')
        return redirect(url_for('employees.index'))

    new_role = request.form['role']
    if employee_service.update_user_role(id, new_role):
        flash('Role updated successfully', 'success')
    else:
        flash('Failed to update role', 'error')
    return redirect(url_for('employees.index'))