# app.py
import os

import requests
from flask import render_template, request, redirect, url_for, flash, Flask

from detector.models import db, Message

app = Flask(__name__)
app.config["ANYMAILFINDER_API_KEY"] = os.getenv("ANYMAILFINDER_API_KEY")
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY")

db.init_app(app)

with app.app_context():
    db.create_all()

# WSGI requires the app to be named "application"
application = app

ANYMAILFINDER_API_KEY = app.config["ANYMAILFINDER_API_KEY"]


# Helper function to validate email using Anymailfinder API
def validate_email(email):
    url = "https://api.anymailfinder.com/v5.0/validate.json"
    headers = {"Authorization": f"Bearer {ANYMAILFINDER_API_KEY}"}
    payload = {"email": email}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            return data.get("validation") in ["valid", "deliverable"]
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False


@app.route("/")
def inbox():
    messages = Message.query.filter_by(is_flagged=False).all()
    return render_template("dashboard.html", messages=messages)


@app.route("/flagged")
def flagged():
    messages = Message.query.filter_by(is_flagged=True).all()
    return render_template("flagged.html", messages=messages)


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
        )
        db.session.add(message)
        db.session.commit()

        flash("Message sent successfully!", "success")
        return redirect(url_for("inbox"))

    return render_template("email.html")
