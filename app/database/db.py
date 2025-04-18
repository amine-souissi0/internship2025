# app/database/db.py

import sqlite3
from config import Config


def get_db():
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    return db