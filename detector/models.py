# models.py
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)  # True if flagged
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"<Message {self.sender_email}>"


class AllowedDomain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<AllowedDomain {self.domain}>"
