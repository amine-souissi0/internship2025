from flask import Blueprint, render_template, request, send_file, session
from flask_login import login_required
import pandas as pd
import os
import urllib.parse  # ✅ This is the missing line!
import io
from flask import make_response

excel_bp = Blueprint('excel', __name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage
parsed_data = None

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

            if filename.endswith('.csv'):
                df = pd.read_csv(file_path, header=[1])
            else:
                df = pd.read_excel(file_path, header=[1])

            df.dropna(how='all', inplace=True)
            df.fillna('', inplace=True)

            # 👉 Save original for logic (unchanged)
            parsed_data = df.copy()

            # 👉 Create display version for preview with blank Unnamed headers
            df_display = df.copy()
            df_display.columns = [
                "" if isinstance(col, str) and col.startswith("Unnamed") else col
                for col in df_display.columns
            ]
            parsed_display_data = df_display

            # 👉 Convert only display version to HTML
            table_html = df_display.to_html(classes='table table-bordered', index=False, border=0, escape=False)

    return render_template('excel/excel.html', table_html=table_html, filename=filename)



@excel_bp.route('/excel/stats')
@login_required
def stats():
    global parsed_data

    if parsed_data is None:
        return render_template('excel/shift_stats.html', stats=None)

    df = parsed_data.copy()

    shift_keywords = [
        "Morning", "Night", "Off", "REST", "MTA", "TOIL", "AL",
        "OFF Day & Replacing Full Evening Shift", "Morning shift & Cont 2nd half Evening replacement"
    ]

    stats_dict = {}

    for _, row in df.iterrows():
        user = row.get("Full Name", "")
        if not user or user in ["nan", "Date", "Day"]:
            continue

        if user not in stats_dict:
            stats_dict[user] = {key: 0 for key in shift_keywords}

        for col in row.index:
            shift = str(row[col]).strip()
            if shift in stats_dict[user]:
                stats_dict[user][shift] += 1

    return render_template('excel/shift_stats.html', stats=stats_dict)



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

    # Extract headers
    week_row = parsed_data.iloc[0]
    day_row = parsed_data.iloc[1]
    date_row = parsed_data.iloc[2]

    user_rows = parsed_data[parsed_data['Full Name'] == user_name]
    if user_rows.empty:
        return "User not found", 404

    shifts = []
    user_row = user_rows.iloc[0]

    for col in parsed_data.columns[3:]:  # Skip metadata columns
        shift = str(user_row[col]).strip()
        if shift.lower() == shift_type.lower():
            # Compose full display string: "Monday - Week 39 - 25/11"
            week_str = str(week_row[col]).strip()
            day_str = str(day_row[col]).strip()
            raw_date_str = str(date_row[col]).strip()

            try:
                formatted_date = pd.to_datetime(raw_date_str, dayfirst=True).strftime('%d/%m')
            except:
                formatted_date = raw_date_str  # fallback

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

    for _, row in df.iterrows():
        user = row.get("Full Name", "")
        if not user or user in ["nan", "Date", "Day"]:
            continue

        if user not in stats_dict:
            stats_dict[user] = {key: 0 for key in shift_keywords}

        for col in row.index:
            shift = str(row[col]).strip()
            if shift in stats_dict[user]:
                stats_dict[user][shift] += 1

    # Convert to DataFrame
    stats_df = pd.DataFrame.from_dict(stats_dict, orient='index')
    stats_df.reset_index(inplace=True)
    stats_df.rename(columns={"index": "User"}, inplace=True)

    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        stats_df.to_excel(writer, index=False, sheet_name='Shift Summary')

    output.seek(0)
    response = make_response(output.read())
    response.headers['Content-Disposition'] = 'attachment; filename=shift_summary.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response



