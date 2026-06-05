from flask import render_template, request, redirect

from db import db
from booking_models import BookingRequest
from . import booking


@booking.route("/", methods=["GET"])
def booking_form():
    return render_template("booking.html")


@booking.route("/submit", methods=["POST"])
def submit_booking():
    item = BookingRequest(
        name=request.form.get("name"),
        company_name=request.form.get("company_name"),
        business_type=request.form.get("business_type"),
        phone=request.form.get("phone"),
        email=request.form.get("email"),
        message=request.form.get("message"),
        status="Ny bokningsförfrågan"
    )

    db.session.add(item)
    db.session.commit()

    return render_template("booking_success.html")