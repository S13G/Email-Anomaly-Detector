# app.py
from flask import Flask, render_template, request, redirect, url_for, flash

from detector.models import db, Message, AllowedDomain

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "3ac32d70cc4f2ffc22523d5d719834be87fdd4d0b2361172205cb1c3c27823c1"
db.init_app(app)

with app.app_context():
    db.create_all()

# WSGI requires the app to be named "application"
application = app


@app.route("/")
def inbox():
    messages = Message.query.filter_by(is_flagged=False).all()
    return render_template("dashboard.html", messages=messages)


@app.route("/flagged")
def flagged():
    messages = Message.query.filter_by(is_flagged=True).all()
    return render_template("flagged.html", messages=messages)


@app.route("/add-domain", methods=["GET", "POST"])
def add_domain():
    if request.method == "POST":
        domain = request.form["domain"]

        if not domain or not domain.startswith("@"):
            flash("Please enter a valid domain (e.g. @example.com).", "danger")
            return redirect(url_for("add_domain"))

        # Check if domain already exists
        existing_domain = AllowedDomain.query.filter_by(domain=domain).first()
        if existing_domain:
            flash("Domain already exists!", "warning")
            return redirect(url_for("add_domain"))
        else:
            new_domain = AllowedDomain(domain=domain)
            db.session.add(new_domain)
            db.session.commit()
            flash("Domain added successfully!", "success")
            return redirect(url_for("inbox"))

    return render_template("add_domain.html")


@app.route("/send", methods=["GET", "POST"])
def send_message():
    if request.method == "POST":
        sender_email = request.form["email"]
        title = request.form["subject"]
        content = request.form["message"]

        if not sender_email or not content:
            flash("Email and content are required!", "danger")
            return redirect(url_for("send_message"))

        # Fetch allowed domains from the database
        allowed_domains = [domain.domain for domain in AllowedDomain.query.all()]
        is_flagged = not any(
            sender_email.endswith(domain) for domain in allowed_domains
        )

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
