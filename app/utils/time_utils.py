# app/utils/time_utils.py

from datetime import datetime, timedelta
import calendar


def parse_time(time_str, format='%H:%M'):
    """Flexible time parsing with fallback"""
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, format)
    except ValueError:
        try:
            return datetime.strptime(time_str, '%I %p')
        except ValueError:
            return None

def format_time(time_str):
    """Format time to 12-hour format with AM/PM"""
    if time_str:
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime('%I:%M %p')
    return None

def hhmm_to_minutes(hhmm):
    """Convert HH:MM formatted string to minutes"""
    sign = 1
    if hhmm.startswith('-'):
        sign = -1
        hhmm = hhmm[1:]
    hours, minutes = map(int, hhmm.split(':'))
    return sign * (hours * 60 + minutes)

def minutes_to_hhmm(minutes):
    """Convert minutes to HH:MM formatted string"""
    sign = '-' if minutes < 0 else ''
    abs_minutes = abs(minutes)
    hours, minutes_remaining = divmod(abs_minutes, 60)
    return f"{sign}{hours:02d}:{minutes_remaining:02d}"

def calculate_overtime_minutes(actual_start, actual_end, shift_start, shift_end):
    """Calculate overtime minutes between actual and expected shift times"""
    if actual_end < actual_start:
        actual_end += timedelta(days=1)
    if shift_end < shift_start:
        shift_end += timedelta(days=1)

    actual_duration = (actual_end - actual_start).total_seconds() / 3600
    shift_duration = (shift_end - shift_start).total_seconds() / 3600
    
    overtime_hours = max(0, actual_duration - shift_duration)
    return int(overtime_hours * 60)

def sum_overtime(overtime_list):
    """Sum up overtime hours from a list of HH:MM formatted strings"""
    total_minutes = sum(hhmm_to_minutes(overtime) for overtime in overtime_list)
    return minutes_to_hhmm(total_minutes)

def get_month_dates(month_offset=0):
    """Get the dates for a month based on the offset from the current month"""
    today = datetime.now().date()
    first_day_of_month = (today.replace(day=1) + relativedelta(months=month_offset))
    _, days_in_month = calendar.monthrange(first_day_of_month.year, first_day_of_month.month)
    return [first_day_of_month + timedelta(days=i) for i in range(days_in_month)]

def get_month_calendar(year, month):
    cal = calendar.Calendar(firstweekday=0)
    month_dates = list(cal.itermonthdates(year, month))
    weeks = []
    for i in range(0, len(month_dates), 7):
        week = month_dates[i:i+7]
        weeks.append(week)
    return weeks

def calculate_month_offset(selected_date, current_date):
    """Calculate the month offset between two dates"""
    return (selected_date.year - current_date.year) * 12 + selected_date.month - current_date.month