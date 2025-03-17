# app/models/user.py

import sqlite3
from flask_login import UserMixin
from config import Config
from cryptography.fernet import Fernet


"""
Represents a user in the system
    :param id: Unique identifier for the user
    :param username: Username of the user
    :param password_hash: Encrypted password hash
    :param employee_id: ID of the associated employee
    :param is_active: Whether the user account is active
    :param role: Role of the user in the system
"""

class User(UserMixin):

    def __init__(self, id, username, password_hash, employee_id, is_active, role):
        self.id = id
        self.username = username
        self.fernet = Fernet(Config.ENCRYPTION_KEY)
        self.password_hash = password_hash
        self._is_active = is_active
        self.role = role
        self.employee_id = employee_id

    def get_id(self):
        return str(self.id)
    
    @property
    def password(self):
        try:
            decrypted = self.fernet.decrypt(self.password_hash.encode()).decode()
            print(f"read password: {decrypted}")
            return decrypted
        except Exception as e:
            print(f"Error decrypting password: {e}")
            return None

    @password.setter
    def password(self, plain_text_password):
        print(f"set password: {plain_text_password}")
        self.password_hash = self.fernet.encrypt(plain_text_password.encode()).decode()

    def check_password(self, password):
        print(f"check_password: {password}")
        try:
            decrypted = self.fernet.decrypt(self.password_hash.encode()).decode()
            print(f"Decrypted password: {decrypted}, Provided password: {password}")
            return decrypted == password
        except Exception as e:
            print(f"Error decrypting password: {str(e)}")
            return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value
        
    def is_manager(self):
        return self.role == 'manager'

    def is_adc_employee(self):
        return self.role == 'adc_employee'