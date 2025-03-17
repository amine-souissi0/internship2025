# app/__init__.py

from flask import Flask, g, redirect, url_for
from flask_login import LoginManager, current_user
from config import Config
from app.services.user_service import get_user_by_id
from .database.db import get_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        try:
            user = get_user_by_id(int(user_id))
            return user
        except Exception as e:
            db.rollback()
            print(f"Error loading user {int(user_id)}: {e}")
        
    
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('my_shifts.index'))
        return redirect(url_for('auth.login'))

    from app.routes import auth, employees, shifts, employee_shift, board, my_shifts, requests
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(employees.employees_bp, url_prefix='/employees')
    app.register_blueprint(shifts.shifts_bp, url_prefix='/shifts')
    app.register_blueprint(employee_shift.employee_shift_bp, url_prefix='/employee_shifts')
    app.register_blueprint(board.board_bp, url_prefix='/board')
    app.register_blueprint(my_shifts.my_shifts_bp, url_prefix='/my_shifts')
    app.register_blueprint(requests.requests_bp, url_prefix='/requests')

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    return app
