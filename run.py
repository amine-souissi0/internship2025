# run.py

from app import create_app
from db_setup import init_db

app = create_app()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)
