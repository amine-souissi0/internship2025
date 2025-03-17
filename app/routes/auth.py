# app/routes/auth.py

from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app.services.user_service import get_user_by_username


auth_bp = Blueprint('auth', __name__)

"""
Handle user login.

GET: Render the login page
POST: Process the login form submission
"""
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"login attempt: {username}, {password}")
        
        user = get_user_by_username(username)
        
        print(f"login user found: {user}")

        if user:
            print(f"User found: id={user.id}, username={user.username}")
            if user.check_password(password):
                print(f"Password check passed for user {username}")
                login_user(user)
                print(f"User {username} logged in successfully")
                return redirect(url_for('my_shifts.index'))
            else:
                print(f"Password check failed for user {username}")
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

"""
Handle user logout.

Log out the current user and redirect to the login page.
"""
@auth_bp.route('/logout')
def logout():
    username = current_user.username if current_user.is_authenticated else None
    logout_user()
    if username:
        flash(f'Goodbye, {username}. You have been logged out.', 'info')
    else:
        flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
