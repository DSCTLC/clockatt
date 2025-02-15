import subprocess
import sys
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

# Function to send email with attachments
def send_email(attachments):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Monthly Attendance Report - Current Month"

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

# Main function to orchestrate the script execution
def main():
    # Run the scripts to generate the reports
    run_scripts()

    # Find all relevant reports for the current month
    reports_dir = '.'  # Directory where reports are saved
    reports = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if
               f.endswith("current.csv") or f.endswith("current.png")]

    # Proceed to send email if there are reports to send
    if reports:
        send_email(reports)
        print("Current month's reports have been sent.")
    else:
        print("No new reports were found for the current month.")

if __name__ == "__main__":
    main()
