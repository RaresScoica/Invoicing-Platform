import datetime
import os
import smtplib
import pytz

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(attachment_file, transactionId):

    # Get SMTP credentials from environmental variables
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    # Email configurations
    bucharest_tz = pytz.timezone('Europe/Bucharest')
    tomorrow_date = (datetime.datetime.now() + datetime.timedelta(days=1)).astimezone(bucharest_tz).strftime('%d.%m.%Y')
    
    sender_email = "rares.goiceanu@arsek.ro"

    #Electric planners:
    #"mihai.sandu@electricplanners.ro" , "romulus@dfg.ro" , "mariust01@yahoo.com"
    #"stefan.diaconu@arsek.ro"
    receiver_emails = ["rares.goiceanu@arsek.ro"]
    receiver_emails_str = ', '.join(receiver_emails)
    subject = "Factura {}".format(transactionId)
    
    # HTML content for the email body
    body = """
    <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .container {{
                    background-color: #f2f2f2;
                    padding: 24px;
                    border-radius: 3px;
                    border: 2px solid #b0c4de;
                }}
                .logo {{
                    text-align: left;
                    margin-right: 10px;
                }}
                .logo a {{
                    text-decoration: none;
                }}
                .logo img {{
                    max-width: 300px;
                    pointer-events: none;
                    -webkit-user-select: none;
                    -moz-user-select: none;
                    -ms-user-select: none;
                    user-select: none;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 3px;
                    margin-top: 20px;
                    color: #333333;
                }}
                p {{
                    margin: 0;
                    line-height: 1.5;
                    font-size: 16px;
                }}
                .spacer1 {{
                    margin-bottom: 20px;
                }}
                .spacer2 {{
                    margin-bottom: 50px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">
                    <a href="https://arsek.ro" target="_self">
                        <img src="cid:logo" alt="Arsek Logo">
                    </a>
                </div>
                <div class="content">
                    <p>Buna ziua,</p>
                    <div class="spacer1"></div>
                    <p>Am atasat factura pentru tranzactia <b>{}</b>.</p>
                    <div class="spacer2"></div> 
                    <p>Multumim,</p>
                    <p>Echipa Arsek Software</p>
                </div>
            </div>
        </body>
    </html>
    """.format(transactionId)
    

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_emails_str
    msg['Subject'] = subject

    # Attach body
    #msg.attach(MIMEBase('text', 'plain'))
    msg.attach(MIMEText(body, 'html'))

    # Attach the logo image
    with open("images/logo_nobg.svg", 'rb') as f:
        logo = MIMEImage(f.read(), _subtype="svg+xml")
        logo.add_header('Content-ID', '<logo>')
        msg.attach(logo)

    # Attach file
    attachment = open(attachment_file, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    # Get just the filename from the attachment_file path
    attachment_filename = os.path.basename(attachment_file)
    
    p.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
    msg.attach(p)

    # Connect to SMTP server and send email
    smtp_server = "smtp.hostinger.com"
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, receiver_emails, msg.as_string())
    print("Email with {} succesfully sent to {}".format(transactionId, receiver_emails_str))
    server.quit()