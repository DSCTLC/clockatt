import subprocess
import sys
import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Mailjet SMTP details
mailjet_api_key = "d4daa32683293aa0cb23b739cbb6dd22"  # Your Mailjet API Key
mailjet_secret_key = "432316725d93f42c72d34aafbf8f2ac1"  # Your Mailjet Secret Key
smtp_server = "in-v3.mailjet.com"
smtp_port = 587  # Use 587 for TLS

# Email details
sender_email = "duanecronje@gmail.com"  # Your email registered with Mailjet
receiver_email = "medcrest@ion.co.za"  # Recipient's email

# Define the paths to the scripts that need to be executed
scripts_to_run = [
    'createcsv.py',
    'main.py',
    'main2.py',
    'previous_m1.py',
    'previous_m2.py'
]

# Define the email log file
log_file_path = 'email_log.txt'

# Function to run other Python scripts with debug output
def run_scripts():
    python_interpreter = sys.executable  # Get the path of the currently running Python interpreter
    for script in scripts_to_run:
        script_path = os.path.join(os.getcwd(), script)  # Ensure the script path is absolute
        print(f"Running {script}...")
        result = subprocess.run([python_interpreter, script_path], capture_output=True, text=True)
        print(f"Output from {script}:")
        print(result.stdout)
        if result.stderr:
            print(f"Errors from {script}:")
            print(result.stderr)
        print(f"Finished running {script}.\n")

# Function to check if the report for the previous month has been sent
def report_already_sent(log_file, target_date):
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            for line in file:
                if target_date in line:
                    return True
    return False

# Function to send email with attachments
def send_email(attachments, target_date):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = f"Monthly Attendance Report for {target_date}"

    for attachment in attachments:
        with open(attachment, "rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment)}")
        msg.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Start TLS encryption
        server.login(mailjet_api_key, mailjet_secret_key)  # Login with your Mailjet API key and Secret key
        server.send_message(msg)  # Send the email

    print("Email sent successfully.")

# Function to update the log file
def update_log(log_file, target_date):
    with open(log_file, "a") as file:
        file.write(f"{target_date}\n")

# Main function to orchestrate the script execution
def main():
    # Determine the target date (previous month)
    today = datetime.datetime.now()
    first_of_this_month = datetime.datetime(today.year, today.month, 1)
    last_of_previous_month = first_of_this_month - datetime.timedelta(days=1)
    target_date = last_of_previous_month.strftime("%m_%Y")

    # Check if the report for the previous month has already been sent
    if not report_already_sent(log_file_path, target_date):
        # Run the scripts to generate the reports
        run_scripts()

        # Find all relevant reports including 'attendance.csv'
        reports_dir='.'  # Directory where reports are saved
        reports=[os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if
                 f.endswith(f"{target_date}.csv") or f.endswith(f"{target_date}.png") or f == "attendance.csv"]

        # Proceed to send email if there are reports to send
        if reports:
            send_email(reports, target_date)
            update_log(log_file_path, target_date)
            print("Reports for", target_date, "have been sent and logged.")
        else:
            print("No new reports were found for", target_date)
    else:
        print("Reports for", target_date, "have already been sent.")

if __name__ == "__main__":
    main()