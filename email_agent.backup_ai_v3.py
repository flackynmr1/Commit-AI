import re
from relevance_engine import analyze_lead, clean, fix_text


def get_attr(obj, name, fallback=""):
    return getattr(obj, name, fallback) or fallback


def build_profile(profile=None):
    profile = profile or {}

    return {
        "sender_name": fix_text(profile.get("sender_name", "Ditt namn")),
        "company_name": fix_text(profile.get("company_name", "Ditt företag")),
        "offer": fix_text(profile.get("offer", "hjälpa företag att få fler kunder")),
        "target_customer": fix_text(profile.get("target_customer", "företag som vill växa")),
        "proof": fix_text(profile.get("proof", "")),
        "phone": clean(profile.get("phone", "")),
        "website": clean(profile.get("website", "")),
        "tone": clean(profile.get("tone", "professionell, enkel och trevlig")),
    }


def create_pitch_for_lead(lead, profile=None, custom_message=None):
    profile = build_profile(profile)

    lead_company = clean(get_attr(lead, "company_name", "ert företag"))
    lead_industry = clean(get_attr(lead, "industry", "er bransch"))
    lead_city = clean(get_attr(lead, "city", ""))

    sender_name = profile["sender_name"]
    sender_company = profile["company_name"]
    proof = profile["proof"]
    phone = profile["phone"]
    website = profile["website"]

    analysis = analyze_lead(lead, profile)

    proof_line = f"\n\nKort bakgrund: {proof}" if proof else ""
    phone_line = f"\nDu når mig även på {phone}." if phone else ""
    website_line = f"\nMer info: {website}" if website else ""

    subject = f"Snabb idé för {lead_company}"

    body = f"""Hej {lead_company},

{analysis["company_insight"]}

{analysis["personal_observation"]} Ofta är utmaningen att {analysis["problem"]}.

På {sender_company} arbetar vi med att {analysis["offer"]} för {analysis["target_customer"]}. För företag som er kan det framför allt hjälpa med att {analysis["value"]}.{proof_line}

Jag ville därför bara höra om det hade varit relevant att jag skickar över ett kort exempel anpassat för er verksamhet?

Vänliga hälsningar,
{sender_name}
{sender_company}{phone_line}{website_line}
"""

    return subject, body.strip()


def create_pitch_for_many(leads, profile=None, custom_message=None):
    results = []
    for lead in leads:
        subject, body = create_pitch_for_lead(lead, profile, custom_message)
        results.append((lead, subject, body))
    return results
