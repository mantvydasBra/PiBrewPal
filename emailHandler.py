import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()
password = os.environ.get("gmail_pass_key")


def send_email(value, treshold, measurementTime, overOrUnder):
   subject = "PiBrewPal Temperature Alert!"
   body = f"Hello, PiBrewPal wants to inform you about temperature which went {overOrUnder} the value of {treshold}°C:\n{measurementTime} | {value}°C"
   sender = "pibrewpal@gmail.com"
   recipients = ["mantaikas16@gmail.com"]


   msg = MIMEText(body)
   msg['Subject'] = subject
   msg['From'] = sender
   msg['To'] = ', '.join(recipients)
   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
      smtp_server.login(sender, password)
      smtp_server.sendmail(sender, recipients, msg.as_string())
   print("Message sent!")
