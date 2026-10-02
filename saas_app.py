from service_profiles import SERVICE_PROFILES, detect_service_type, get_service_profile
import os
from functools import wraps
from flask import Flask, render_template, session, redirect, request

from config import config
from db import db
from dotenv import load_dotenv

load_dotenv()

ADMIN_PASSWORD = "vpv77"


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.secret_key = os.getenv("SECRET_KEY", "flerkunder-dev-secret")

    db.init_app(app)

    try:
        from auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix="/auth")
    except Exception as e:
        print("Auth disabled:", e)

    try:
        from billing import billing as billing_blueprint
        app.register_blueprint(billing_blueprint, url_prefix="/billing")
    except Exception as e:
        print("Billing disabled:", e)

    try:
        from chatbot import chatbot as chatbot_blueprint
        app.register_blueprint(chatbot_blueprint, url_prefix="/chatbot")
    except Exception as e:
        print("Chatbot disabled:", e)

    try:
        from admin import admin as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix="/admin")
    except Exception as e:
        print("Admin disabled:", e)

    try:
        from widgets import widgets as widgets_blueprint
        app.register_blueprint(widgets_blueprint, url_prefix="/widgets")
    except Exception as e:
        print("Widgets disabled:", e)

    try:
        from leads import leads as leads_blueprint
        app.register_blueprint(leads_blueprint, url_prefix="/leads")
    except Exception as e:
        print("Leads disabled:", e)
    try:
        from leads import leads as leads_blueprint
        # DUPLICATE REMOVED: app.register_blueprint(leads_blueprint, url_prefix="/leads")
    except Exception as e:
        print("Leads disabled:", e)

    try:
        from booking import booking as booking_blueprint
        app.register_blueprint(booking_blueprint, url_prefix="/booking")
    except Exception as e:
        print("Booking disabled:", e)

    with app.app_context():
        db.create_all()
    def admin_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("admin_logged_in") is True:
                return f(*args, **kwargs)
            return redirect("/admin-login")

        return wrapper


    def approved_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("admin_logged_in") is True:
                return f(*args, **kwargs)

            if session.get("user_id"):
                return f(*args, **kwargs)

            return redirect("/auth/login-page")

        return wrapper

    @app.route("/")
    def index():
        return render_template("flerkunder_home.html")

    @app.route("/pricing")
    def pricing():
        return render_template("flerkunder_home.html")

    @app.route("/checkout/<plan>")
    def checkout(plan):
        plans = {
            "starter": {"name": "Starter", "price": "299", "leads": "100"},
            "growth": {"name": "Growth", "price": "699", "leads": "600"},
            "agency": {"name": "Agency", "price": "1499", "leads": "2000"},
        }

        selected = plans.get(plan, plans["starter"])
        return render_template("checkout.html", plan=selected)

    @app.route("/dashboard")
    def dashboard():
        from leads.routes import get_usage_context

        return render_template(
            "user_dashboard.html",
            usage=get_usage_context()
        )

    @app.route("/lead-agent")
    def user_lead_agent():
        if not session.get("user_id"):
            return redirect("/auth/login-page")

        from leads.routes import get_usage_context, LEAD_OPTIONS
        from lead_models import Lead

        all_leads = Lead.query.order_by(Lead.created_at.desc()).all()

        return render_template(
            "user_lead_agent.html",
            usage=get_usage_context(),
            lead_options=LEAD_OPTIONS,
            leads=all_leads
        )
    @app.route("/profile-setup", methods=["GET", "POST"])
    @app.route("/company-profile", methods=["GET", "POST"])
    @app.route("/foretagsprofil", methods=["GET", "POST"])
    def profile_setup():
        if request.method == "POST":
            session["company_name"] = request.form.get("company_name")
            session["service_type"] = request.form.get("service_type")
            session["target_area"] = request.form.get("target_area")
            return redirect("/dashboard")

        return render_template(
            "profile_setup.html",
            services=SERVICE_PROFILES
        )


    @app.route("/checklist")
    @approved_required
    def checklist():
        return render_template("checklist.html")

    @app.route("/admin-login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "GET":
            return render_template("admin_login.html")

        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin-portal")

        return render_template("admin_login.html", error="Fel lösenord")

    @app.route("/admin-portal")
    @admin_required
    def admin_portal():
        bookings = []
        leads = []

        try:
            from booking_models import BookingRequest
            bookings = BookingRequest.query.order_by(
                BookingRequest.created_at.desc()
            ).all()
        except Exception as e:
            print("Could not load bookings:", e)

        try:
            from lead_models import Lead
            leads = Lead.query.order_by(
                Lead.created_at.desc()
            ).all()
        except Exception as e:
            print("Could not load leads:", e)

        return render_template(
            "admin_portal.html",
            bookings=bookings,
            leads=leads
        )

    @app.route("/admin-logout")
    def admin_logout():
        session.clear()
        return redirect("/")
    # SAFE_REDIRECT_ROUTES
    @app.route("/leads-old")
    def leads_old_redirect():
        return redirect("/lead-agent")

    @app.route("/home")
    def home_redirect():
        return redirect("/")

    @app.route("/start")
    def start_redirect():
        return redirect("/")



    return app


app = create_app()


@app.route("/google4d43ec67c07761aa.html")
def google_verify():
    return "google-site-verification: google4d43ec67c07761aa.html", 200, {"Content-Type": "text/plain"}

@app.route("/sitemap.xml")
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.flerkunder.site/</loc>
  </url>
</urlset>"""
    return xml, 200, {"Content-Type": "application/xml"}
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5050)),
        debug=False
    )














