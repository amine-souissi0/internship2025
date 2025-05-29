from flask import Blueprint, render_template, request, send_file, session
from flask_login import login_required
import pandas as pd
import os
import urllib.parse
import io
from flask import make_response

excel_bp = Blueprint('excel', __name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage
parsed_data = None
parsed_display_data = None

@excel_bp.route('/excel/', methods=['GET', 'POST'])
@login_required
def index():
    global parsed_data, parsed_display_data
    table_html = None
    filename = None

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xlsx', '.xls', '.csv')):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            filename = file.filename

            # Read the CSV file with correct header
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path, skiprows=5, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)
                df = df.fillna('')
                df.columns = [col.strip() for col in df.columns]
            else:
                df = pd.read_excel(file_path, header=[1])
                df = df.dropna(how='all')
                df = df.fillna('')

            parsed_data = df.copy()

            print("Parsed Data Columns:", parsed_data.columns.tolist())
            print("Parsed Data Head:\n", parsed_data.head())

            df_display = df.copy()
            df_display.columns = [
                "" if isinstance(col, str) and col.startswith("Unnamed") else col
                for col in df_display.columns
            ]
            parsed_display_data = df_display

            table_html = df_display.to_html(classes='table table-bordered', index=False, border=0, escape=False)

    return render_template('excel/excel.html', table_html=table_html, filename=filename)

@excel_bp.route('/excel/stats')
@login_required
def stats():
    global parsed_data

    if parsed_data is None:
        print("No parsed data available in stats route.")
        return render_template('excel/shift_stats.html', stats=None)

    df = parsed_data.copy()

    print("Stats DataFrame Columns:", df.columns.tolist())
    print("Stats DataFrame Head:\n", df.head())

    shift_keywords = [
        "Morning", "Night", "Off", "REST", "MTA", "TOIL", "AL", "MC", "Half Day Off",
        "OFF Day & Replacing Full Evening Shift", "Morning shift & Cont 2nd half Evening replacement"
    ]

    stats_dict = {}
    total_shifts = {key: 0 for key in shift_keywords}

    if "Full Name" not in df.columns:
        print("Full Name column not found in DataFrame. Available columns:", df.columns.tolist())
        return render_template('excel/shift_stats.html', stats=None)

    full_name_idx = df.columns.get_loc("Full Name")
    print(f"Full Name column index: {full_name_idx}")

    for _, row in df.iterrows():
        user = row.get("Full Name", "")
        if not user or user in ["nan", "", "Legend", "Public Holidays MYS"]:
            continue

        if user not in stats_dict:
            stats_dict[user] = {key: 0 for key in shift_keywords}

        for col in df.columns[full_name_idx + 1:]:
            if col == "Days Working from 1st Sept - 30th Sept":
                break
            shift = str(row[col]).strip()
            if shift in stats_dict[user]:
                stats_dict[user][shift] += 1
                total_shifts[shift] += 1

        stats_dict[user]["MC"] = int(row.get("MC", 0)) if str(row.get("MC", "")) != "" else 0
        stats_dict[user]["Half Day Off"] = int(row.get("Half Day Off", 0)) if str(row.get("Half Day Off", "")) != "" else 0
        stats_dict[user]["MTA"] = int(row.get("MTA", 0)) if str(row.get("MTA", "")) != "" else 0
        stats_dict[user]["TOIL"] = int(row.get("Total TOIL from 1st Sept", 0)) if str(row.get("Total TOIL from 1st Sept", "")) != "" else 0

    if not stats_dict:
        print("No valid user data found to process stats.")
        return render_template('excel/shift_stats.html', stats=None)

    print("Stats Dictionary:", stats_dict)
    print("Total Shifts:", total_shifts)
    users = list(stats_dict.keys())
    return render_template('excel/shift_stats.html', stats=stats_dict, users=users, stats_dict=stats_dict)

@excel_bp.route('/excel/download/<filename>')
@login_required
def download_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

@excel_bp.route('/excel/details/<user_name>/<shift_type>')
@login_required
def shift_details(user_name, shift_type):
    global parsed_data

    user_name = urllib.parse.unquote(user_name)

    if parsed_data is None:
        return "No shift data available", 404

    week_row = parsed_data.iloc[0] if len(parsed_data) > 0 else pd.Series()
    day_row = parsed_data.iloc[1] if len(parsed_data) > 1 else pd.Series()
    date_row = parsed_data.iloc[2] if len(parsed_data) > 2 else pd.Series()

    user_rows = parsed_data[parsed_data['Full Name'] == user_name]
    if user_rows.empty:
        return "User not found", 404

    shifts = []
    user_row = user_rows.iloc[0]

    full_name_idx = parsed_data.columns.get_loc("Full Name")
    for col in parsed_data.columns[full_name_idx + 1:]:
        if col == "Days Working from 1st Sept - 30th Sept":
            break
        shift = str(user_row[col]).strip()
        if shift.lower() == shift_type.lower():
            week_str = str(week_row[col]).strip() if col in week_row else ""
            day_str = str(day_row[col]).strip() if col in day_row else ""
            raw_date_str = str(date_row[col]).strip() if col in date_row else ""

            try:
                formatted_date = pd.to_datetime(raw_date_str, dayfirst=True).strftime('%d/%m')
            except:
                formatted_date = raw_date_str

            full_display = f"{day_str} - {week_str} - {formatted_date}"

            shifts.append({
                "datetime": full_display,
                "type": shift
            })

    return render_template("excel/shift_details.html", user_name=user_name, shift_type=shift_type, shifts=shifts)

@excel_bp.route('/excel/stats/export', endpoint='export_stats')
@login_required
def export_stats():
    global parsed_data

    if parsed_data is None:
        return "No data available", 404

    df = parsed_data.copy()

    shift_keywords = [
        "Morning", "Night", "Off", "REST", "MTA", "TOIL", "AL",
        "OFF Day & Replacing Full Evening Shift", "Morning shift & Cont 2nd half Evening replacement"
    ]

    stats_dict = {}

    full_name_idx = df.columns.get_loc("Full Name")
    for _, row in df.iterrows():
        user = row.get("Full Name", "")
        if not user or user in ["nan", "", "Legend", "Public Holidays MYS"]:
            continue

        if user not in stats_dict:
            stats_dict[user] = {key: 0 for key in shift_keywords}

        for col in df.columns[full_name_idx + 1:]:
            if col == "Days Working from 1st Sept - 30th Sept":
                break
            shift = str(row[col]).strip()
            if shift in stats_dict[user]:
                stats_dict[user][shift] += 1

    stats_df = pd.DataFrame.from_dict(stats_dict, orient='index')
    stats_df.reset_index(inplace=True)
    stats_df.rename(columns={"index": "User"}, inplace=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        stats_df.to_excel(writer, index=False, sheet_name='Shift Summary')

    output.seek(0)
    response = make_response(output.read())
    response.headers['Content-Disposition'] = 'attachment; filename=shift_summary.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response