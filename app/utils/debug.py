# app/utils/debug.py

from app import get_db

############
# For Debug 
############ 


def get_detailed_employee_shift(id):
    db = get_db()
    print(f"get_detailed_employee_shift({id})")
    try:
        row = db.execute('''
            SELECT 
                es.id, 
                es.employee_id, 
                es.request_status,
                e.first_name, 
                e.last_name,
                s.name AS shift_name
            FROM employee_shift es
            JOIN employees e ON es.employee_id = e.id
            JOIN shifts s ON es.shift_id = s.id
            WHERE es.id = ?
        ''', (id,)).fetchone()
        
        if row:
            es_info = {
                'id': row['id'],
                'employee_id': row['employee_id'],
                'employee_fullname': f"{row['first_name']} {row['last_name']}",
                'shift_name': row['shift_name'],
                'request_status': row['request_status']
            }
            
            print(f"Employee Shift Details: ID {es_info['id']}, Employee ID {es_info['employee_id']}")
            print(f"Employee Name {es_info['employee_fullname']}, Shift Name: {es_info['shift_name']}, Request Status: {es_info['request_status']}")
            
            return es_info
        else:
            print(f"No employee shift found with ID: {id}")
            return None
    except Exception as e:
        print(f"Error fetching detailed employee shift: {e}")
        return None
    finally:
        db.close()