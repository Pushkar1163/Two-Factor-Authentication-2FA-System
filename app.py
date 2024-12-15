import pyotp
from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "your_secret_key"


users_db = {}


def send_email_otp(email, otp):
    sender = "enter your gmail" 
    recipient = email
    subject = "Your OTP Code"
    body = f"Your OTP code is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  
            server.starttls()  
            server.login("enter your email", "your_app_password")  
            server.sendmail(sender, recipient, msg.as_string())
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Check your credentials or App Password.")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        
        totp = pyotp.TOTP(pyotp.random_base32())
        secret = totp.secret
        users_db[username] = {'password': password, 'email': email, 'totp_secret': secret}

       
        otp = pyotp.TOTP(secret).now()
        send_email_otp(email, otp)

        return redirect(url_for('verify', username=username))
    return render_template('register.html')


@app.route('/verify/<username>', methods=['GET', 'POST'])
def verify(username):
    if request.method == 'POST':
        password = request.form['password']
        otp = request.form['otp']

        user = users_db.get(username)

        
        if user and user['password'] == password:
            
            totp = pyotp.TOTP(user['totp_secret'])
            if totp.verify(otp):
                return "Login successful"
            else:
                flash('Invalid OTP!')
        else:
            flash('Invalid password!')
    return render_template('verify.html')


@app.route('/')
def index():
    return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug=True)
