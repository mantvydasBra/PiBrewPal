import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Get Gmail app pass key from .env file
password = os.environ.get("gmail_pass_key")

def send_email(value, treshold, measurementTime, overOrUnder):
   # Define email template
   subject = "PiBrewPal Temperature Alert!"
   body = f"Hello, PiBrewPal wants to inform you about temperature which went {overOrUnder} the value of {treshold}°C:\n{measurementTime} | {value}°C"
   sender = "pibrewpal@gmail.com"
   recipients = ["mantaikas16@gmail.com"]

   # Set email variables
   msg = MIMEText(body)
   msg['Subject'] = subject
   msg['From'] = sender
   msg['To'] = ', '.join(recipients)

   # Connect to smtp gmail server
   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
      smtp_server.login(sender, password)
      smtp_server.sendmail(sender, recipients, msg.as_string())
   print("Message sent!")
