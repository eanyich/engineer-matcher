import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

def send_notification(data, ticket):
    # Logic to send an email notification
    # ...
    engineer = data["engineer"]
    matched_score = data["matching_score"]

    smtp_server = os.getenv('SMTP_SERVER')
    smtp_email = os.getenv('SMTP_EMAIL')
    
    # Code to send an email notification to the engineer's manager
    # ...
    print(f"Engineer: {engineer}\nMatched Score: {matched_score}\nTicket: {ticket}\n" + "-"*50 + "\n")

