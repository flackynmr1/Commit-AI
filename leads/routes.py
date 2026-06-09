from service_profiles import SERVICE_PROFILES

from ai_research_agent import create_ai_research_pitch
from email_history_models import EmailHistory
from flask import render_template, request, redirect, url_for, session, flash

from email_finder import find_email_from_website
from db import db
from lead_models import Lead
from lead_agent import generate_demo_leads
from email_agent import create_pitch_for_lead
from calendar_agent import create_google_calendar_link

try:
    from models import User
except Exception:
    User = None

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


LEAD_OPTIONS = [5, 20, 50, 100, 200, 500]


def get_current_user():
    if User is None:
        return None

    user_id = session.get("user_id")
    if not user_id:
        return None

    return User.query.get(user_id)


def get_usage_context():
    user = get_current_user()

    if user:
        return {
            "plan": getattr(user, "plan", "free_trial"),
            "leads_used": getattr(user, "leads_used", 0),
            "leads_limit": getattr(user, "leads_limit", 5),
            "remaining_leads": user.remaining_leads() if hasattr(user, "remaining_leads") else 5,
            "max_leads_per_search": getattr(user, "max_leads_per_search", 5),
            "gmail_connected": getattr(user, "gmail_connected", False),
            "logged_in": True,
            "free_trial": getattr(user, "plan", "free_trial") == "free_trial",
        }

    free_used = session.get("free_leads_used", 0)
    free_limit = 5

    return {
        "plan": "free_trial",
        "leads_used": free_used,
        "leads_limit": free_limit,
        "remaining_leads": max(0, free_limit - free_used),
        "max_leads_per_search": 5,
        "gmail_connected": "gmail_token" in session,
        "logged_in": False,
        "free_trial": True,
    }


def has_gemini_ai_research():
    usage = get_usage_context()
    plan = usage.get("plan", "free_trial").lower()
    return plan in ["growth", "agency"]


def charge_leads(amount):
    user = get_current_user()

    if user:
        user.leads_used = getattr(user, "leads_used", 0) + amount
        db.session.commit()
        return

    session["free_leads_used"] = session.get("free_leads_used", 0) + amount
    session.modified = True


def profile_is_ready():
    profile = session.get("company_profile", {})
    return bool(profile.get("company_name") and profile.get("offer"))


def create_pitch_by_plan(lead, profile, custom_message=""):
    if has_gemini_ai_research():
        return create_ai_research_pitch(lead, profile)

    return create_pitch_for_lead(
        lead=lead,
        profile=profile,
        custom_message=custom_message,
    )


@leads.route("/", methods=["GET"])
def lead_dashboard():
    all_leads = Lead.query.order_by(Lead.created_at.desc()).all()

    return render_template(
        "user_lead_agent.html",
        leads=all_leads,
        usage=get_usage_context(),
        lead_options=LEAD_OPTIONS,
        profile=session.get("company_profile", {}), services=SERVICE_PROFILES,
    )


@leads.route("/find", methods=["POST"])
def find_leads():
    city = request.form.get("city", "Malmö")
    industry = request.form.get("industry", "flyttfirma")

    try:
        requested_limit = int(request.form.get("lead_limit", 5))
    except Exception:
        requested_limit = 5

    usage = get_usage_context()
    remaining = usage["remaining_leads"]
    max_per_search = usage["max_leads_per_search"]

    if remaining <= 0:
        if usage["free_trial"]:
            flash("Du har använt dina 5 gratis leads. Välj ett paket för att fortsätta.", "warning")
        else:
            flash("Din lead-limit är slut för denna månad.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    if requested_limit not in LEAD_OPTIONS:
        requested_limit = 5

    actual_limit = min(requested_limit, remaining, max_per_search)

    found_leads = []

    if search_places:
        try:
            found_leads = search_places(
                city=city,
                industry=industry,
                limit=actual_limit,
            )
        except TypeError:
            found_leads = search_places(
                city=city,
                industry=industry,
            )[:actual_limit]
        except Exception as e:
            print("Google Places failed:", e)

    if not found_leads:
        found_leads = generate_demo_leads(
            city=city,
            industry=industry,
        )[:actual_limit]

    created = 0

    for item in found_leads[:actual_limit]:
        exists = Lead.query.filter_by(
            company_name=item.get("company_name")
        ).first()

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
        created += 1

    db.session.commit()

    if created > 0:
        charge_leads(created)

    flash(
        f"Hittade {created} leads. Du har {get_usage_context()['remaining_leads']} leads kvar.",
        "success",
    )

    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/profile/setup", methods=["GET", "POST"])
def profile_setup():
    if request.method == "POST":
        session["company_profile"] = {
            "sender_name": request.form.get("sender_name", ""),
            "company_name": request.form.get("company_name", ""),
            "offer": request.form.get("offer", ""),
            "target_customer": request.form.get("target_customer", ""),
            "proof": request.form.get("proof", ""),
            "phone": request.form.get("phone", ""),
            "website": request.form.get("website", ""),
        }

        session.modified = True

        flash("Företagsprofil sparad. Nu skapas pitchar med din företagsinfo.", "success")
        return redirect(url_for("leads.lead_dashboard"))

    return render_template(
        "profile_setup.html",
        profile=session.get("company_profile", {}), services=SERVICE_PROFILES,
    )


@leads.route("/pitch/<int:lead_id>", methods=["POST"])
def create_pitch(lead_id):
    if not profile_is_ready():
        flash("Fyll i din företagsprofil först så AI:n kan skriva personliga mail.", "warning")
        return redirect(url_for("leads.profile_setup"))

    lead = Lead.query.get_or_404(lead_id)

    profile = session.get("company_profile", {})
    custom_message = request.form.get("custom_message", "")

    subject, body = create_pitch_by_plan(
        lead=lead,
        profile=profile,
        custom_message=custom_message,
    )

    lead.email_subject = subject
    lead.email_body = body
    lead.status = "Gemini AI Pitch skapad" if has_gemini_ai_research() else "Pitch skapad"

    db.session.commit()

    flash("Pitch skapad.", "success")
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/pitch-all", methods=["POST"])
def pitch_all():
    if not profile_is_ready():
        flash("Fyll i din företagsprofil först så AI:n kan skriva personliga mail.", "warning")
        return redirect(url_for("leads.profile_setup"))

    all_leads = Lead.query.all()
    profile = session.get("company_profile", {})
    custom_message = request.form.get("custom_message", "")

    created_count = 0

    for lead in all_leads:
        subject, body = create_pitch_by_plan(
            lead=lead,
            profile=profile,
            custom_message=custom_message,
        )

        lead.email_subject = subject
        lead.email_body = body
        lead.status = "Gemini AI Pitch skapad" if has_gemini_ai_research() else "Pitch skapad"
        created_count += 1

    db.session.commit()

    if has_gemini_ai_research():
        flash(f"Skapade {created_count} Gemini AI Research-pitchar.", "success")
    else:
        flash(f"Skapade {created_count} vanliga pitchar.", "success")

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


@leads.route("/find-email-all", methods=["POST"])
def find_email_all():
    all_leads = Lead.query.all()
    found = 0
    skipped = 0

    for lead in all_leads:
        if lead.email or not lead.website:
            skipped += 1
            continue

        email = find_email_from_website(lead.website)

        if email:
            lead.email = email
            found += 1
        else:
            skipped += 1

    db.session.commit()

    flash(f"Hittade {found} emails. Hoppade över {skipped}.", "success")
    return redirect(url_for("leads.lead_dashboard"))



@leads.route("/gmail/disconnect")
def gmail_disconnect():
    session.pop("gmail_token", None)

    user = get_current_user()
    if user and hasattr(user, "gmail_connected"):
        user.gmail_connected = False
        db.session.commit()

    flash("Gmail kopplades bort. Välj nytt Gmail-konto.", "success")
    return redirect(url_for("leads.gmail_connect"))

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

    user = get_current_user()

    if user and hasattr(user, "gmail_connected"):
        user.gmail_connected = True
        db.session.commit()

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
        lead.email_subject or f"Snabb fråga till {lead.company_name}",
        lead.email_body,
    )

    lead.status = "Gmail-utkast skapat"
    db.session.commit()

    flash("Gmail-utkast skapat.", "success")
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/gmail/draft-all", methods=["POST"])
def gmail_draft_all():
    if create_gmail_draft is None:
        flash("Gmail service är inte konfigurerad.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    if "gmail_token" not in session:
        return redirect(url_for("leads.gmail_connect"))

    all_leads = Lead.query.all()
    created = 0
    skipped = 0

    for lead in all_leads:
        if not lead.email or not lead.email_body:
            skipped += 1
            continue

        create_gmail_draft(
            session["gmail_token"],
            lead.email,
            lead.email_subject or f"Snabb fråga till {lead.company_name}",
            lead.email_body,
        )

        lead.status = "Gmail-utkast skapat"
        created += 1

    db.session.commit()

    flash(f"Skapade {created} Gmail-utkast. Hoppade över {skipped}.", "success")
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/gmail/draft-all-and-archive", methods=["POST"])
def gmail_draft_all_and_archive():
    if create_gmail_draft is None:
        flash("Gmail service är inte konfigurerad.", "warning")
        return redirect(url_for("leads.lead_dashboard"))

    if "gmail_token" not in session:
        return redirect(url_for("leads.gmail_connect"))

    all_leads = Lead.query.all()
    created = 0
    skipped = 0

    for lead in all_leads:
        if not lead.email or not lead.email_body:
            skipped += 1
            continue

        create_gmail_draft(
            session["gmail_token"],
            lead.email,
            lead.email_subject or f"Snabb fråga till {lead.company_name}",
            lead.email_body,
        )

        history = EmailHistory(
            company_name=lead.company_name,
            industry=lead.industry,
            city=lead.city,
            website=lead.website,
            phone=lead.phone,
            email=lead.email,
            source=lead.source,
            email_subject=lead.email_subject,
            email_body=lead.email_body,
            action="Gmail-utkast skapat",
        )

        db.session.add(history)
        db.session.delete(lead)
        created += 1

    db.session.commit()

    flash(
        f"Skapade {created} Gmail-utkast och flyttade dem till historik. Hoppade över {skipped}.",
        "success",
    )

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



@leads.route("/delete-all", methods=["POST"])
def delete_all_leads():
    Lead.query.delete()
    db.session.commit()
    flash("Alla leads har rensats.", "success")
    return redirect(url_for("leads.lead_dashboard"))


@leads.route("/admin/fill-leads/<password>/<int:amount>")
def fill_test_leads(password, amount):
    if password != "test123":
        return "Fel losenord", 403

    if User is None:
        return "User model hittades inte", 500

    users = User.query.all()
    if not users:
        return "Inga users hittades", 404

    for user in users:
        user.leads_used = 0
        user.leads_limit = amount
        user.max_leads_per_search = amount
        user.plan = "free_trial"

    session["test_leads_override"] = amount
    session["test_max_per_search"] = amount

    db.session.commit()

    return f"Klart. Alla users fick {amount} leads."
@leads.route("/history", methods=["GET"])
def email_history():
    history = EmailHistory.query.order_by(
        EmailHistory.created_at.desc()
    ).all()

    return render_template("email_history.html", history=history)















