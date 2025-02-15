# Adjusting the script 'main2.py' to generate reports for the current month

# Import necessary libraries
import json
import pandas as pd
from datetime import datetime
import calendar
import matplotlib.pyplot as plt

# Function to determine the first and last day of the current month
def get_current_month_range():
    today = datetime.now()
    first_day_of_current_month = datetime(today.year, today.month, 1)
    last_day_of_current_month = today
    return first_day_of_current_month, last_day_of_current_month

# Function to process and generate the report
def generate_report():
    # Get current month range
    first_day_of_current_month, last_day_of_current_month = get_current_month_range()

    # Read data from the JSON file
    with open('attendance_log.json', 'r') as file:
        data = json.load(file)

    # Convert timestamps to datetime objects and sort the data
    for entry in data:
        entry['timestamp'] = datetime.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
    data.sort(key=lambda x: x['timestamp'])

    # Filter data for the current month
    data = [entry for entry in data if first_day_of_current_month <= entry['timestamp'] <= last_day_of_current_month]

    # Group data by employee and sort by timestamp
    grouped_data = {}
    for entry in data:
        employee = entry['employee']
        if employee not in grouped_data:
            grouped_data[employee] = []
        grouped_data[employee].append(entry)

    # Prepare data for DataFrame
    report_data = []
    monthly_totals = {employee: 0 for employee in grouped_data}
    for employee, entries in grouped_data.items():
        daily_records = {}
        for entry in entries:
            date = entry['timestamp'].date()
            if date not in daily_records:
                daily_records[date] = []
            daily_records[date].append(entry['timestamp'])

        for date in pd.date_range(start=first_day_of_current_month, end=last_day_of_current_month):
            if date.date() in daily_records:
                times = daily_records[date.date()]
                times_str = ", ".join(time.strftime("%H:%M") for time in times)
                if len(times) % 2 == 1:  # Ignore the last time if an odd number of timestamps
                    times = times[:-1]
                total_hours = sum((times[i+1] - times[i]).seconds / 3600 for i in range(0, len(times), 2))
                monthly_totals[employee] += total_hours
                report_data.append([employee, date.date(), times_str, f"{total_hours:.2f} Hours"])
            else:
                report_data.append([employee, date.date(), "No Times Logged", "0 Hours"])

    # Add monthly totals to the report
    for employee in monthly_totals:
        report_data.append([employee, 'Total for Month', '', f"{monthly_totals[employee]:.2f} Hours"])

    # Create DataFrame and save to CSV
    report_df = pd.DataFrame(report_data, columns=['Employee', 'Date', 'Times', 'Total Hours'])
    month_year_str = first_day_of_current_month.strftime("%m_%Y")
    csv_filename = f'monthly_attendance_report_{month_year_str}.csv'
    report_df.to_csv(csv_filename, index=False)

    # Generate graphical reports with color coding
    unique_employees = report_df['Employee'].unique()
    for employee in unique_employees:
        employee_data = report_df[(report_df['Employee'] == employee) & (report_df['Date'] != 'Total for Month')]
        employee_rows = [["Date", "Times", "Total Hours"]]
        cell_colors = []

        for _, row in employee_data.iterrows():
            if row['Times'] == "No Times Logged":
                color = '#FFFF00'  # Yellow
            elif "Hours" in row['Total Hours'] and float(row['Total Hours'].split()[0]) > 0:
                color = '#DDFFDD'  # Light Green
            else:
                color = '#FFDDDD'  # Light Red
            employee_rows.append([row['Date'], row['Times'], row['Total Hours']])
            cell_colors.append([color] * 3)

        # Create a figure and axis for each employee
        fig, ax = plt.subplots(figsize=(20, 2 + 0.5 * len(employee_rows)))
        ax.axis('tight')
        ax.axis('off')
        title = f"Attendance Report for {employee} (Current)"
        ax.set_title(title, fontsize=16, pad=20)

        # Create the table for each employee
        table = ax.table(cellText=employee_rows, colLabels=employee_rows.pop(0), loc='center', cellLoc='center', cellColours=cell_colors)
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.4)

        plt.subplots_adjust(left=0.2, top=0.9, bottom=0.1)
        employee_name_formatted = employee.replace(" ", "_").replace(".", "")
        png_filename = f'attendance_report_{employee_name_formatted}_current.png'
        plt.savefig(png_filename, bbox_inches='tight')
        plt.close()

    print("CSV and graphical reports generated for each employee.")

# Uncomment the following line to run the function
generate_report()