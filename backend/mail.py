import smtplib
from email.message import EmailMessage
import os
from datetime import datetime

def send_email():
    today = datetime.now().strftime("%d-%m-%Y")  # Ensure the date format matches
    filename = f"attendance/attendance_{today}.xlsx"  # Build the filename with the correct date format

    # Check if the file exists
    if not os.path.exists(filename):
        print(f"[ERROR] Attendance file not found: {filename}")
        return
    else:
        print(f"[INFO] File exists: {filename}")

    # Set up the email content
    msg = EmailMessage()
    msg['Subject'] = f'Attendance Report - {today}'
    msg['From'] = 'munannurusaiyasasvi@gmail.com'
    msg['To'] = 'personal7353@gmail.com'
    msg.set_content(f"Attached is the attendance report for {today}.")

    # Attach the file
    try:
        with open(filename, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=os.path.basename(filename))

        # Set up the SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('munannurusaiyasasvi@gmail.com', 'qmkecxevuwvnzjmr')  # Gmail App Password
        server.send_message(msg)
        server.quit()
        print("[INFO] Email sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
