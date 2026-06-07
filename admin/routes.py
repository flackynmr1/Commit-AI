
from datetime import datetime, timedelta

from flask import jsonify, render_template, redirect, session
from . import admin
from models import User, Customer, Conversation, db
from booking_models import BookingRequest


PLAN_CONFIG = {
    "starter": {
        "leads_limit": 100,
        "max_leads_per_search": 50,
    },
    "growth": {
        "leads_limit": 600,
        "max_leads_per_search": 100,
    },
    "agency": {
        "leads_limit": 2000,
        "max_leads_per_search": 500,
    },
}


def admin_required():
    return session.get("role") == "admin" or session.get("admin_logged_in") is True


def activate_user_plan(user, plan):
    plan = plan.lower()

    if plan not in PLAN_CONFIG:
        plan = "starter"

    config = PLAN_CONFIG[plan]

    user.plan = plan
    user.subscription_tier = plan
    user.leads_limit = config["leads_limit"]
    user.max_leads_per_search = config["max_leads_per_search"]
    user.leads_used = 0

    if hasattr(user, "access_expires_at"):
        user.access_expires_at = datetime.utcnow() + timedelta(days=30)


@admin.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Admin module is running",
    })


@admin.route("/stats", methods=["GET"])
def stats():
    return jsonify({
        "users": User.query.count(),
        "customers": Customer.query.count(),
        "conversations": Conversation.query.count(),
        "bookings": BookingRequest.query.count(),
    })


@admin.route("/portal")
def portal():
    if not admin_required():
        return redirect("/admin-login")

    users = User.query.order_by(User.created_at.desc()).all()
    bookings = BookingRequest.query.order_by(
        BookingRequest.created_at.desc()
    ).all()

    return render_template(
        "admin_portal.html",
        users=users,
        bookings=bookings,
    )


@admin.route("/activate/<int:user_id>/<string:plan>", methods=["POST", "GET"])
def activate_plan(user_id, plan):
    if not admin_required():
        return redirect("/admin-login")

    user = User.query.get_or_404(user_id)
    activate_user_plan(user, plan)

    db.session.commit()
    return redirect("/admin/portal")


@admin.route("/reset-leads/<int:user_id>", methods=["POST", "GET"])
def reset_leads(user_id):
    if not admin_required():
        return redirect("/admin-login")

    user = User.query.get_or_404(user_id)
    user.leads_used = 0

    db.session.commit()
    return redirect("/admin/portal")


@admin.route("/deactivate/<int:user_id>", methods=["POST", "GET"])
def deactivate_user(user_id):
    if not admin_required():
        return redirect("/admin-login")

    user = User.query.get_or_404(user_id)

    user.plan = "free_trial"
    user.subscription_tier = "free_trial"
    user.leads_limit = 5
    user.max_leads_per_search = 5
    user.leads_used = 0

    if hasattr(user, "access_expires_at"):
        user.access_expires_at = datetime.utcnow()

    db.session.commit()
    return redirect("/admin/portal")


@admin.route("/approve/<int:user_id>")
def approve_user(user_id):
    if not admin_required():
        return redirect("/admin-login")

    user = User.query.get_or_404(user_id)
    activate_user_plan(user, "starter")

    db.session.commit()
    return redirect("/admin/portal")


@admin.route("/make-admin/<int:user_id>")
def make_admin(user_id):
    if not admin_required():
        return redirect("/admin-login")

    user = User.query.get_or_404(user_id)
    user.role = "admin"
    activate_user_plan(user, "agency")

    db.session.commit()
    return redirect("/admin/portal")


@admin.route("/booking-status/<int:booking_id>/<string:status>", methods=["POST", "GET"])
def booking_status(booking_id, status):
    if not admin_required():
        return redirect("/admin-login")

    booking = BookingRequest.query.get_or_404(booking_id)

    status_map = {
        "Ny": "Ny bokningsfÃ¶rfrÃ¥gan",
        "Kontaktad": "Kontaktad",
        "MÃ¶te bokat": "MÃ¶te bokat",
        "StÃ¤ngd": "StÃ¤ngd",
    }

    booking.status = status_map.get(status, status)

    db.session.commit()
    return redirect("/admin/portal")

