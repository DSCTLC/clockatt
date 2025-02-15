import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Automatically determine the current date and the first day of the current month
today = datetime.now()
first_day_of_current_month = datetime(today.year, today.month, 1)

# Function to check if the timestamp is from the current month
def is_from_current_month(timestamp):
    entry_date = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
    return entry_date >= first_day_of_current_month and entry_date <= today

# Read data from the JSON file
with open('attendance_log.json', 'r') as file:
    data = json.load(file)

# Filter data for the current month
filtered_data = [entry for entry in data if is_from_current_month(entry['timestamp'])]

# Group data by employee and sort by timestamp
grouped_data = {}
for entry in filtered_data:
    employee = entry['employee']
    if employee not in grouped_data:
        grouped_data[employee] = []
    grouped_data[employee].append(entry)
for employee in grouped_data:
    grouped_data[employee].sort(key=lambda x: x['timestamp'])

# Create a DataFrame for CSV data
csv_data = []
for employee, entries in grouped_data.items():
    for entry in entries:
        timestamp = datetime.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
        csv_data.append([employee, timestamp.date(), timestamp, entry['status'], entry.get('type', ''), entry.get('login_type', '')])

# Convert to DataFrame and save as CSV
csv_df = pd.DataFrame(csv_data, columns=['Employee', 'Date', 'Timestamp', 'Status', 'Type', 'LoginType'])
csv_df.to_csv('attendance_current_month.csv', index=False)

# Read the generated CSV
df = pd.read_csv('attendance_current_month.csv', parse_dates=['Date', 'Timestamp'])

# Define specific times for comparison
morning_cutoff = datetime.strptime("09:05", "%H:%M").time()
evening_cutoff = datetime.strptime("17:55", "%H:%M").time()

# Initialize a dictionary to hold legend labels and their corresponding colors
legend_labels = {}

# Filter data for the current month
df = df[(df['Date'] >= first_day_of_current_month) & (df['Date'] <= today)]

# Process each employee
unique_employees = df['Employee'].unique()
for employee in unique_employees:
    employee_df = df[df['Employee'] == employee]

    # Plotting
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_xlim(first_day_of_current_month, today)
    ax.set_ylim(7, 21)
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Add horizontal lines at 09:00 and 18:00
    ax.axhline(y=9, color='red', linestyle='--')
    ax.axhline(y=18, color='red', linestyle='--')

    # Group by date for plotting bars
    daily_records = employee_df.groupby(employee_df['Date'].dt.date)
    for date, records in daily_records:
        times = records['Timestamp'].tolist()
        late_arrival = False
        early_departure = False
        for i in range(0, len(times), 2):
            in_time = times[i]
            out_time = times[i + 1] if i + 1 < len(times) else None
            if out_time:
                start_hour = in_time.hour + in_time.minute / 60
                end_hour = out_time.hour + out_time.minute / 60

                # Check for late arrival and early departure
                if in_time.time() > morning_cutoff:
                    late_arrival = True
                if out_time.time() < evening_cutoff:
                    early_departure = True

                # Determine bar color and update legend
                bar_color = 'green'  # Default color for regular hours
                if late_arrival and early_departure:
                    bar_color = 'red'
                    legend_labels['Late Arrival & Early Departure'] = bar_color
                elif late_arrival:
                    bar_color = 'orange'
                    legend_labels['Late Arrival'] = bar_color
                elif early_departure:
                    bar_color = 'purple'
                    legend_labels['Early Departure'] = bar_color

                ax.bar(date, end_hour - start_hour, bottom=start_hour, width=0.1, align='edge', color=bar_color, edgecolor='black')

    # Create legend from the legend_labels dictionary
    legend_patches = [plt.Rectangle((0,0),1,1, color=color) for color in legend_labels.values()]
    ax.legend(legend_patches, legend_labels.keys(), loc='upper left')

    # Set labels and title
    ax.set_title(f'Work Hours for {employee} - Current Month')
    ax.set_xlabel('Date')
    ax.set_ylabel('Hours of the Day')

    # Set date labels vertically
    plt.xticks(rotation=90)

    # Save and close the plot
    plt.savefig(f'{employee}_work_hours_current.png', bbox_inches='tight')
    plt.close()

print("Plots have been generated for each employee for the current month.")
