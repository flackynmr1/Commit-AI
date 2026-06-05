from datetime import datetime
from db import db


class BookingRequest(db.Model):
    __tablename__ = "booking_requests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Ny bokningsförfrågan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)