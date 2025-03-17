# adc_webapp

The idea is to build a simple app for managing shifts of employee in a company.

## To start the app from terminal:
source ./venv/bin/activate
pip install -r requirements.txt
python run.py

or flask run


## Features
### Done
crud tables for users, employees, shifts and employee_shifts
login/logout
board
approval requests

### To Do
Fixes
Overtime
shift constraints

## Tech Stack
Frontend: HTML/CSS
Backend: Python
DB: sqlite3

## Architecture
Architecture:
adc_webapp/
│
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── database.db
│   │   └── db.py
│   ├── models/
│   │   ├── employee_shift.py
│   │   ├── employee.py
│   │   ├── shift.py
│   │   └── user.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── board.py
│   │   ├── employee_shift.py
│   │   ├── employees.py
│   │   ├── my_shifts.py
│   │   ├── requests.py
│   │   └── shifts.py
│   ├── services/
│   │   ├── employee_service.py
│   │   ├── employee_shift_service.py
│   │   ├── my_shifts_service.py
│   │   ├── requests_service.py
│   │   └── shift_service.py
│   ├── static/
│   └── templates/
│       ├── board/
│       │   └── board.html
│       ├── employee_shifts/
│       │   ├── edit_employee_shift.html
│       │   └── employee_shifts.py
│       ├── board/
│       │   ├── board.html
│       │   ├── board.py
│       ├── board/
│       │   ├── board.html
│       │   ├── board.py
│       ├── requests_service.py
│       └── shift_service.py
│
├── config.py
├── run.py
├── db_setup.py
├── README.md
└── requirements.txt

  
TODO:
just minute for start and end time
sort by team
extra shift selection: medical leave, MTA, time off, ... (see excel) + custom input

if time off selected, then send request to manager approval (email ?)
