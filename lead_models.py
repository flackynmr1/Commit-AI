from datetime import datetime
from db import db


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(180), nullable=True)
    source = db.Column(db.String(120), default="demo")
    status = db.Column(db.String(50), default="Ny Lead")
    email_subject = db.Column(db.String(255), nullable=True)
    email_body = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

   