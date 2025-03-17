# app/models/employee.py

"""
Represents an employee in the system.
    :param first: First name of the employee
    :param last: Last name of the employee
    :param team: Team the employee belongs to
    :param emp_id: Unique identifier for the employee
"""
class Employee:

    def __init__(self, first, last, team, emp_id):
        self.id = emp_id
        self.first = first
        self.last = last
        self.team = team

    @property
    def fullname(self):
        return f'{self.first} {self.last}'

    def __repr__(self):
        return f"Employee('{self.first}', '{self.last}', '{self.team}')"

    
