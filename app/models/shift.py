# app/models/team.py

"""
Represents a shift in the system.
    :param name: Name of the shift
    :param bg_color: background color code for the shift
    :param text_color: text color code for the shift
    :param start_time: Start time of the shift
    :param end_time: End time of the shift
    :param id: Unique identifier for the shift (optional)
    :param is_active: Whether the shift is active or not (default: True)
"""

class Shift:
    def __init__(self, name, bg_color, text_color, start_time, end_time, id=None, is_active=True):
        self.id = id
        self.name = name
        self.bg_color = bg_color
        self.text_color = text_color
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = is_active

    @property
    def start_hour(self):
        return self.start_time.split()[0]

    @property
    def start_period(self):
        return self.start_time.split()[1]

    @property
    def end_hour(self):
        return self.end_time.split()[0]

    @property
    def end_period(self):
        return self.end_time.split()[1]
