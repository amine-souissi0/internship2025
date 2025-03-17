# config.py

import os
from cryptography.fernet import Fernet

class Config:
    SECRET_KEY = 'my-secret-key'
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app','database', 'database.db')    
    ENCRYPTION_KEY = b'ojLTgW21lQNG4KWMpksqch4LGwm-sVd9_o4t4YdJwyY='
    
# username="joshu"
# password="rnd"