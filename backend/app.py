import base64
import certifi
import os
import requests
import json
import time
import pdfkit
import datetime
import smtplib

from dotenv import load_dotenv
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, redirect, render_template, request, jsonify, send_file, send_from_directory, session, url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

frontend_folder = os.path.join(os.path.dirname(__file__), '../frontend')
app = Flask(__name__, template_folder=os.path.join(frontend_folder, 'templates'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
uri = os.getenv('MONGO_URI')

if 'DYNO' in os.environ:  # if running on Heroku
    wkhtmltopdf_path = '/app/bin/wkhtmltopdf'
else:
    wkhtmltopdf_path = os.getenv('WKHTMLTOPDF_PATH')

# Configuration for pdfkit
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/<int:transactionId>')
def transaction(transactionId):
    return render_template('index.html', transactionId=transactionId)

@app.route('/success')
def success():
    # Fetch session storage data
    email = session.get('email')
    company_details = session.get('company_details')
    transactionId = session.get('transactionId')

    try:
        transactionId = int(transactionId)

    except Exception as e:
        return redirect(url_for('index'))

    db = client['EV_Stations']
    collection = db['transactions']

    transactionDetails = collection.find_one({"TransactionID": transactionId})

    if transactionDetails == None:
        return redirect(url_for('index'))
    
    # Get the current date
    formatted_time = transactionDetails["StopTime"]
    # Parse the input string into a datetime object
    parsed_time = datetime.strptime(formatted_time, "%Y-%m-%dT%H:%M:%SZ")
    # Format the datetime object in the desired format
    current_date = parsed_time.strftime("%d/%m/%Y %H:%M")

    if 'DYNO' in os.environ:  # if running on Heroku
        with open('/app/frontend/images/dfg_logo.png', 'rb') as f:
            image_data = f.read()
    else:
        with open('../frontend/images/dfg_logo.png', 'rb') as f:
            image_data = f.read()

    # Convert image data to base64-encoded string
    base64_image = base64.b64encode(image_data).decode('utf-8')

    # Render the HTML template for the invoice and pass session storage data
    html = render_template('invoice.html', image_data=base64_image, email=email, company_details=company_details, transactionDetails=transactionDetails, current_date=current_date)

    if 'DYNO' in os.environ:  # if running on Heroku
        # Convert HTML to PDF and save to the temporary file
        pdfkit.from_string(html, f"/app/backend/facturi/factura_{transactionId}.pdf", configuration=config)

        send_emails(f"/app/backend/facturi/factura_{transactionId}.pdf", transactionId, email)
    else:
        # Convert HTML to PDF and save to the temporary file
        pdfkit.from_string(html, f"facturi/factura_{transactionId}.pdf", configuration=config)

        send_emails(f"facturi/factura_{transactionId}.pdf", transactionId, email)

    # Send the PDF file as a downloadable attachment
    # return send_file(f"facturi/factura_{transactionId}.pdf", as_attachment=True)
    return render_template('success.html', email=email)

def remove_alpha_chars(s):
    """Remove non-digit characters from a string."""
    return ''.join(filter(str.isdigit, s))

def fetch_anaf_data(cui, attempts=2):
    """Fetch company data from ANAF API with retry on empty 'found'."""
    url = "https://webservicesp.anaf.ro/PlatitorTvaRest/api/v8/ws/tva"
    headers = {'Content-Type': 'application/json'}
    data = [{"cui": int(remove_alpha_chars(cui)), "data": datetime.now().strftime("%Y-%m-%d")}]
    
    for attempt in range(attempts):
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('found'):
                    return result
                else:
                    print("Empty 'found' array, retrying...")
                    time.sleep(1.5)  # Wait for 1.5 seconds before retrying
            except json.JSONDecodeError:
                print("Failed to decode JSON. Response was:")
                print(response.text)
                return {}
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
            return {}

    print("Maximum attempts reached, returning last response.")
    return {}

# Function to save JSON data to a temporary file
def save_json(data):
    if 'DYNO' in os.environ:  # if running on Heroku
        file_location = "/tmp/anaf_response.json"
    else:
        file_location = "C:/Users/developer/Documents/ws-server/platform/temp/anaf_response.json"  # Define temporary file path
    with open(file_location, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return file_location

@app.route('/send_email_and_cui', methods=['POST'])
def send_email_and_cui():
    if 'DYNO' in os.environ:  # if running on Heroku
        file_path = "/tmp/anaf_response.json"
    else:
        file_path = '../temp/anaf_response.json'
    if os.path.exists(file_path):
        os.remove(file_path)

    data = request.json
    cui = data.get('cui')
    email = data.get('email')
    transactionId = data.get('transactionId')

    session['email'] = email
    session['transactionId'] = transactionId
    
    if cui:
        cui_variable = cui
        anaf_response = fetch_anaf_data(cui_variable)
        if anaf_response:
            file_location = save_json(anaf_response)
            print(f"Data saved to {file_location}")
            return jsonify({'file_location': file_location})
        else:
            return render_template('index.html')

    return jsonify({'message': 'CUI not provided'}), 400

@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.json
    email = data.get('email')
    transactionId = data.get('transactionId')

    session['email'] = email
    session['transactionId'] = transactionId

    return jsonify({'message': 'Data Received'})

@app.route('/send_company_details', methods=['POST'])
def send_company_details():
    data = request.json
    email = data.get('email')
    company_details = data.get('company')

    # Store email and company details in the session
    session['email'] = email
    session['company_details'] = company_details

    return 'Company details received successfully'

@app.route('/get_temp_file/<path:filename>')
def get_temp_file(filename):
    if 'DYNO' in os.environ:  # if running on Heroku
        file_path = "/tmp/anaf_response.json"
    else:
        file_path = '../temp/anaf_response.json'
    if os.path.exists(file_path):
        # Serve the temporary file to the client
        if 'DYNO' in os.environ:  # if running on Heroku
            return send_from_directory('/tmp', filename)
        else:
            return send_from_directory('C:/Users/developer/Documents/ws-server/platform/temp', filename)
    else:
        print("CUI not found")
        return redirect(url_for('index'))
    
def send_emails(attachment_file, transactionId, email):
    # Get SMTP credentials from environmental variables
    smtp_username = "rares.goiceanu@arsek.ro"
    smtp_password = "jdm,Bass2000"
    
    sender_email = "rares.goiceanu@arsek.ro"

    #Electric planners:
    #"mihai.sandu@electricplanners.ro" , "romulus@dfg.ro" , "mariust01@yahoo.com"
    #"stefan.diaconu@arsek.ro"
    receiver_emails = [email, "rares.goiceanu@arsek.ro"]
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

    if 'DYNO' in os.environ:  # if running on Heroku
        # Attach the logo image
        with open("/app/frontend/images/logo_nobg.png", 'rb') as f:
            logo = MIMEImage(f.read(), _subtype="svg+xml")
            logo.add_header('Content-ID', '<logo>')
            msg.attach(logo)
    else:
        # Attach the logo image
        with open("../frontend/images/logo_nobg.png", 'rb') as f:
            logo = MIMEImage(f.read(), _subtype="svg+xml")
            logo.add_header('Content-ID', '<logo>')
            msg.attach(logo)

    # Attach file
    print(attachment_file)
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
    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    