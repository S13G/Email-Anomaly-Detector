# app.py
import os

import requests
from flask import render_template, request, redirect, url_for, flash, Flask, abort
from flask_mail import Mail, Message as MailMessage

from detector.models import db, Message

app = Flask(__name__)
app.config["ANYMAILFINDER_API_KEY"] = os.getenv("ANYMAILFINDER_API_KEY")
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Flask-Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"  # Replace with your mail server
app.config["MAIL_PORT"] = 465  # Use 465 for SSL, 587 for TLS
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_EMAIL")  # Your email
app.config["MAIL_PASSWORD"] = os.getenv(
    "MAIL_PASSWORD"
)  # Your email password or app password

print(app.config["MAIL_PASSWORD"])
print(app.config["MAIL_USERNAME"])

mail = Mail(app)

app.secret_key = os.getenv("SECRET_KEY")

db.init_app(app)

with app.app_context():
    db.create_all()

# WSGI requires the app to be named "application"
application = app

ANYMAILFINDER_API_KEY = app.config["ANYMAILFINDER_API_KEY"]

flagged_message = None


# Helper function to validate email using Anymailfinder API
def validate_email(email):
    url = "https://api.anymailfinder.com/v5.0/validate.json"
    headers = {"Authorization": f"Bearer {ANYMAILFINDER_API_KEY}"}
    payload = {"email": email}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("validation") == "valid":
                return True
            else:
                global flagged_message
                response_message = data.get("validation")

                if response_message == "invalid":
                    flagged_message = "The email address provided is invalid, either a typo error or a wrong account. Please check for typos or use a different email address."
                elif response_message == "unknown":
                    flagged_message = "The validity of the email address and domain could not be confirmed. Please double-check the email or try another one."
                return False
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False


@app.route("/")
def inbox():
    messages = Message.query.filter_by(is_flagged=False).order_by(
        Message.timestamp.desc()
    )
    return render_template("dashboard.html", messages=messages)


@app.route("/flagged")
def flagged():
    messages = Message.query.filter_by(is_flagged=True).order_by(
        Message.timestamp.desc()
    )
    return render_template("flagged.html", messages=messages)


@app.route("/email/<int:email_id>")
def email_detail(email_id):
    message = Message.query.get(email_id)

    # If the email doesn't exist, return a 404 page
    if not message:
        abort(404)

    return render_template("email_detail.html", message=message)


@app.route("/send", methods=["GET", "POST"])
def send_message():
    if request.method == "POST":
        sender_email = request.form["email"]
        title = request.form["subject"]
        content = request.form["message"]

        if not sender_email or not content:
            flash("Email and content are required!", "danger")
            return redirect(url_for("send_message"))

        # Validate the email
        is_flagged = not validate_email(sender_email)

        # Save the message
        message = Message(
            sender_email=sender_email,
            title=title,
            content=content,
            is_flagged=is_flagged,
            flagged_message=flagged_message,
        )
        db.session.add(message)
        db.session.commit()

        # Send the email only if it is not flagged
        if not is_flagged:
            try:
                email_message = MailMessage(
                    subject=title,
                    sender=app.config["MAIL_USERNAME"],
                    recipients=[sender_email],
                    body=content,
                )
                mail.send(email_message)
                flash("Message sent successfully!", "success")
            except Exception as e:
                print(e)
                flash(f"Failed to send email: {str(e)}", "danger")
        else:
            flash("Message flagged and not sent due to validation issues.", "warning")

        return redirect(url_for("inbox"))

    return render_template("email.html")
