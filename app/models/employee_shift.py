# app/models/employee_shift.py

"""
Represents an employee's shift assignment.
    :param id: Unique identifier for the employee shift
    :param employee_id: ID of the employee assigned to the shift
    :param shift_id: ID of the shift assigned to the employee
    :param date: Date of the shift
    :param actual_start_time: Actual time the employee started the shift (optional)
    :param actual_end_time: Actual time the employee ended the shift (optional)
    :param overtime_hours: Number of overtime hours worked for this specific shift (default: 0)
    :param request_status: Status of any requests related to this shift (default: 'NONE')
"""

class EmployeeShift:
    def __init__(self,
                 id,
                 employee_id,
                 shift_id,
                 date,
                 actual_start_time=None,
                 actual_end_time=None,
                 overtime_hours='00:00',
                 request_status='NONE',
                 start_time='00:00',
                 end_time='00:00',
                 shift_type='Regular',
                 custom_details=None,
                 approval_status='Approved'):
        self.id = id
        self.employee_id = employee_id
        self.shift_id = shift_id
        self.date = date
        self.actual_start_time = actual_start_time
        self.actual_end_time = actual_end_time
        self.overtime_hours = overtime_hours
        self.request_status = request_status
        self.start_time = start_time
        self.end_time = end_time
        self.shift_type = shift_type
        self.custom_details = custom_details
        self.approval_status = approval_status
    
    def format_overtime(self):
        return self.overtime_hours
  
    def get_display_status(self, shift_name):
        if shift_name and shift_name.upper() in ['REST', 'OFF']:
            return self.approval_status
        return 'Approved'