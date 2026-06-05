from flask import jsonify, render_template, session, redirect
from . import admin
from models import User, Customer, Conversation, db
from booking_models import BookingRequest


def admin_required():
    return session.get("role") == "admin"


@admin.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Admin module is running'
    })


@admin.route('/stats', methods=['GET'])
def stats():
    return jsonify({
        'users': User.query.count(),
        'customers': Customer.query.count(),
        'conversations': Conversation.query.count(),
        'bookings': BookingRequest.query.count()
    })


@admin.route("/portal")
def portal():
    if not admin_required():
        return redirect("/auth/login")

    users = User.query.order_by(User.created_at.desc()).all()
    bookings = BookingRequest.query.order_by(BookingRequest.created_at.desc()).all()

    return render_template("admin_portal.html", users=users, bookings=bookings)


@admin.route("/approve/<int:user_id>")
def approve_user(user_id):
    if not admin_required():
        return redirect("/auth/login")

    user = User.query.get_or_404(user_id)
    user.subscription_tier = "approved"
    db.session.commit()

    return redirect("/admin/portal")


@admin.route("/make-admin/<int:user_id>")
def make_admin(user_id):
    if not admin_required():
        return redirect("/auth/login")

    user = User.query.get_or_404(user_id)
    user.role = "admin"
    user.subscription_tier = "approved"
    db.session.commit()

    return redirect("/admin/portal")


@admin.route("/booking-status/<int:booking_id>/<string:status>", methods=["POST"])
def booking_status(booking_id, status):
    if not admin_required():
        return redirect("/auth/login")

    booking = BookingRequest.query.get_or_404(booking_id)
    # Normalize status to match expected values
    status_map = {
        "Ny": "Ny bokningsförfrågan",
        "Kontaktad": "Kontaktad",
        "Möte bokat": "Möte bokat",
        "Stängd": "Stängd"
    }
    # If status is already a full status, use it; otherwise map
    if status in status_map:
        booking.status = status_map[status]
    else:
        # Assume it's already a full status
        booking.status = status
    db.session.commit()
    return redirect("/admin/portal")