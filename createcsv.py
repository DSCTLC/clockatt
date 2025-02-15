import json
from datetime import datetime, timedelta
import csv


def is_from_previous_month(timestamp, first_day, last_day):
    entry_date=datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
    return first_day <= entry_date <= last_day


def create_csv_from_attendance(attendance_log_path, output_csv_path):
    # Calculate the first and last day of the previous month
    today=datetime.now()
    first_day_of_previous_month=datetime(today.year, today.month, 1) - timedelta(days=1)
    first_day_of_previous_month=first_day_of_previous_month.replace(day=1)
    last_day_of_previous_month=datetime(today.year, today.month, 1) - timedelta(days=1)

    # Read attendance data
    with open(attendance_log_path, 'r') as file:
        data=json.load(file)

    # Filter and group data
    filtered_data={}
    for entry in data:
        if is_from_previous_month(entry['timestamp'], first_day_of_previous_month, last_day_of_previous_month):
            employee=entry['employee']
            date=datetime.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%S.%f').date()
            if employee not in filtered_data:
                filtered_data[employee]={}
            if date not in filtered_data[employee]:
                filtered_data[employee][date]=[]
            filtered_data[employee][date].append(entry['timestamp'])

    # Prepare data for CSV
    csv_rows=[['Employee', 'Date'] + ['Time' + str(i) for i in range(1, 21)]]
    for employee, dates in filtered_data.items():
        for date, timestamps in dates.items():
            row=[employee, date.strftime('%Y-%m-%d')]
            times=[datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f').time().strftime('%H:%M') for timestamp in
                   sorted(timestamps)]
            row.extend(times)
            row.extend([''] * (20 - len(times)))  # Fill remaining cells with blanks
            csv_rows.append(row)

    # Write CSV
    output_file=f'{output_csv_path}monthly_attendance_report_{first_day_of_previous_month.strftime("%m_%Y")}.csv'
    with open(output_file, 'w', newline='') as file:
        writer=csv.writer(file)
        writer.writerows(csv_rows)  # Corrected this line

    print(f'CSV file has been created: {output_file}')


# Example usage
if __name__ == '__main__':
    create_csv_from_attendance('attendance_log.json', './')
