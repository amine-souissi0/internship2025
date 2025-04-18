# app/routes/requests.py

"""
Shift Request Management Routes

This module handles the management of shift requests, providing routes for:
- / (view_requests): List all shift requests (manager only)
- /request/<id>: Submit a new shift request (REST or OFF)
- /approve/<id>: Approve a shift request (manager only)
- /reject/<id>: Reject a shift request (manager only)
"""

from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.services import requests_service, my_shifts_service
from flask_login import login_required, current_user

requests_bp = Blueprint('requests', __name__)


@requests_bp.route('/')
def view_requests():
    if not current_user.is_manager():
        flash('You do not have permission to view this page', 'error')
        return redirect(url_for('main.index'))
    
    requests = requests_service.get_all_requests()
    return render_template('requests/requests.html', requests=requests, active='requests')

@requests_bp.route('/request/<int:id>', methods=['POST'])
@login_required
def request_approval(id):
    request_type = request.form['request_type']
    if request_type in ['REST', 'OFF']:
        if requests_service.update_request_status(id, 'REQUESTED'):
            flash(f'{request_type} request submitted successfully', 'success')
        else:
            flash('Failed to submit request', 'error')
    return redirect(url_for('my_shifts.index'))

@requests_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
def approve_request(id):
    if not current_user.is_manager():
        flash('You do not have permission to perform this action', 'error')
        return redirect(url_for('main.index'))
    
    if requests_service.approve_request(id):
        flash('Request approved successfully', 'success')
    else:
        flash('Failed to approve request', 'error')
    return redirect(url_for('requests.view_requests'))

@requests_bp.route('/reject/<int:id>', methods=['POST'])
@login_required
def reject_request(id):
    if not current_user.is_manager():
        flash('You do not have permission to perform this action', 'error')
        return redirect(url_for('main.index'))
    
    if requests_service.reject_request(id):
        flash('Request reject successfully', 'success')
    else:
        flash('Failed to reject request', 'error')
    return redirect(url_for('requests.view_requests'))

def reset_pending_shifts(employee_id):
    db = get_db()
    db.execute(
        '''
        UPDATE employee_shift
        SET approval_status = 'Pending'
        WHERE employee_id = ? AND shift_type IN ('OFF', 'REST')
        ''',
        (employee_id,)
    )
    db.commit()