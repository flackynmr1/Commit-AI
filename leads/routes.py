from flask import render_template, request, redirect, url_for, session, flash

from email_finder import find_email_from_website
from db import db
from lead_models import Lead
from lead_agent import generate_demo_leads
from email_agent import create_pitch_for_lead
from calendar_agent import create_google_calendar_link

try:
    from places_service import search_places
except Exception:
    search_places = None

try:
    from gmail_service import get_gmail_flow, create_gmail_draft
except Exception:
    get_gmail_flow = None
    create_gmail_draft = None

from . import leads


@leads.route("/", methods=["GET"])
def lead_dashboard():
    all_leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template("leads.html", leads=all_leads)


@leads.route("/find", methods=["POST"])
def find_leads():
    city = request.form.get("city", "Malmö")
    industry = request.form.get("industry", "flyttfirma")

    found_leads = []

    if search_places:
        try:
            found_leads = search_places(city=city, industry=industry)
        except Exception as e:
            print("Google Places failed:", e)

    if not found_leads:
        found_leads = generate_demo_leads(city=city, industry=industry)

    for item in found_leads:
        exists = Lead.query.filter_by(company_name=item.get("company_name")).first()
        if exists:
            continue

        lead = Lead(
            company_name=item.get("company_name"),
            industry=item.get("industry", industry),
            city=item.get("city", city),
            website=item.get("website", ""),
            phone=item.get("phone", ""),
            email=item.get("email", ""),
            source=item.get("source", "Google Places"),
            status="Ny Lead",
        )
        db.session.add(lead)

    db.session.commit()
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/pitch/<int:lead_id>", methods=["POST"])
def create_pitch(lead_id):
    lead = Lead.query.get_or_404(lead_id)

    subject, body = create_pitch_for_lead(lead)

    lead.email_subject = subject
    lead.email_body = body
    lead.status = "Pitch skapad"

    db.session.commit()
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/pitch-all", methods=["POST"])
def pitch_all():
    all_leads = Lead.query.all()
    created_count = 0

    for lead in all_leads:
        subject, body = create_pitch_for_lead(lead)
        lead.email_subject = subject
        lead.email_body = body
        lead.status = "Pitch skapad"
        created_count += 1

    db.session.commit()
    flash(f"Skapade pitchar för {created_count} leads.", "success")
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/ready-mail/<int:lead_id>", methods=["POST"])
def ready_mail(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    lead.status = "Mail redo"
    db.session.commit()
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/mark-sent/<int:lead_id>", methods=["POST"])
def mark_sent(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    lead.status = "Mail skickat"
    db.session.commit()
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/meeting/<int:lead_id>", methods=["GET"])
def meeting(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    lead.status = "Möte på gång"
    db.session.commit()
    return redirect(create_google_calendar_link(lead.company_name))


@leads.route("/delete/<int:lead_id>", methods=["POST"])
def delete_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/find-email/<int:lead_id>", methods=["POST"])
def find_email(lead_id):
    lead = Lead.query.get_or_404(lead_id)

    if not lead.website:
        flash("Lead saknar hemsida.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    email = find_email_from_website(lead.website)

    if email:
        lead.email = email
        db.session.commit()
        flash(f"Hittade email: {email}", "success")
    else:
        flash("Kunde inte hitta email på hemsidan.", "warning")

    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/gmail/connect")
def gmail_connect():
    if get_gmail_flow is None:
        flash("Gmail service är inte konfigurerad.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    flow = get_gmail_flow()
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )
    return redirect(auth_url)


@leads.route("/gmail/callback")
def gmail_callback():
    if get_gmail_flow is None:
        flash("Gmail service är inte konfigurerad.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    flow = get_gmail_flow()
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials

    session["gmail_token"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    flash("Gmail kopplat.", "success")
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/gmail/draft/<int:lead_id>", methods=["POST"])
def gmail_draft(lead_id):
    lead = Lead.query.get_or_404(lead_id)

    if create_gmail_draft is None:
        flash("Gmail service är inte konfigurerad.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    if "gmail_token" not in session:
        return redirect(url_for("leads.gmail_connect"))

    if not lead.email:
        flash("Lead saknar email. Gmail-utkast kan inte skapas.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    if not lead.email_body:
        flash("Skapa pitch först.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    create_gmail_draft(
        session["gmail_token"],
        lead.email,
        lead.email_subject or f"Fler kunder till {lead.company_name}",
        lead.email_body,
    )

    lead.status = "Gmail-utkast skapat"
    db.session.commit()

    flash("Gmail-utkast skapat.", "success")
    return redirect(url_for("leads.lead_dashboard"))