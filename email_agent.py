from relevance_engine import (
    build_relevance_sentence,
    build_pitch_angle,
    build_cta,
)


def clean(value, fallback=""):
    if value is None:
        return fallback

    value = str(value).strip()
    return value if value else fallback


def get_attr(obj, name, fallback=""):
    return clean(getattr(obj, name, fallback), fallback)


def build_profile(profile=None):
    if profile is None:
        profile = {}

    return {
        "sender_name": clean(profile.get("sender_name"), "Ditt namn"),
        "company_name": clean(profile.get("company_name"), "Ditt företag"),
        "offer": clean(profile.get("offer"), "våra tjänster"),
        "target_customer": clean(
            profile.get("target_customer"),
            "företag och privatpersoner"
        ),
        "proof": clean(profile.get("proof"), ""),
        "phone": clean(profile.get("phone"), ""),
        "website": clean(profile.get("website"), ""),
    }


def make_lead_obj(lead_company, lead_industry, lead_city, lead_website):
    return type("LeadObj", (), {
        "company_name": lead_company,
        "industry": lead_industry,
        "city": lead_city,
        "website": lead_website,
    })()


def create_pitch_for_lead(lead, profile=None, custom_message=None):
    profile = build_profile(profile)

    lead_company = get_attr(lead, "company_name", "ert företag")
    lead_industry = get_attr(lead, "industry", "er bransch")
    lead_city = get_attr(lead, "city", "Sverige")
    lead_website = get_attr(lead, "website", "")

    lead_obj = make_lead_obj(
        lead_company,
        lead_industry,
        lead_city,
        lead_website,
    )

    if custom_message and clean(custom_message):
        return rewrite_custom_email(
            lead_obj=lead_obj,
            profile=profile,
            custom_message=custom_message,
        )

    return create_default_email(
        lead_obj=lead_obj,
        profile=profile,
    )


def create_default_email(lead_obj, profile):
    lead_company = clean(lead_obj.company_name, "ert företag")

    sender_name = profile["sender_name"]
    sender_company = profile["company_name"]
    offer = profile["offer"]
    target_customer = profile["target_customer"]
    proof = profile["proof"]
    phone = profile["phone"]
    website = profile["website"]

    subject = create_subject(lead_obj, profile)

    relevance_sentence = build_relevance_sentence(lead_obj, profile)
    angle = build_pitch_angle(lead_obj, profile)
    cta = build_cta(lead_obj, profile)

    proof_line = ""
    if proof:
        proof_line = f"\n\nKort om oss: {proof}"

    contact_lines = build_contact_lines(phone, website)

    body = f"""Hej {lead_company},

{relevance_sentence}

Jag heter {sender_name} och representerar {sender_company}. Vi arbetar med {offer} för {target_customer}.{proof_line}

Jag tänkte därför höra om {angle} är något som kan vara aktuellt för er, antingen nu eller längre fram.

{cta.capitalize()}

Med vänliga hälsningar
{sender_name}
{sender_company}{contact_lines}
"""

    return subject, body


def rewrite_custom_email(lead_obj, profile, custom_message):
    lead_company = clean(lead_obj.company_name, "ert företag")
    lead_industry = clean(lead_obj.industry, "er bransch")
    lead_city = clean(lead_obj.city, "Sverige")

    sender_name = profile["sender_name"]
    sender_company = profile["company_name"]
    offer = profile["offer"]
    target_customer = profile["target_customer"]
    proof = profile["proof"]
    phone = profile["phone"]
    website = profile["website"]

    subject = create_subject(lead_obj, profile)

    relevance_sentence = build_relevance_sentence(lead_obj, profile)

    proof_line = ""
    if proof:
        proof_line = f"\n\nKort om oss: {proof}"

    contact_lines = build_contact_lines(phone, website)

    improved_message = improve_custom_message(
        message=custom_message,
        lead_company=lead_company,
        lead_industry=lead_industry,
        lead_city=lead_city,
        sender_company=sender_company,
        offer=offer,
        target_customer=target_customer,
    )

    body = f"""Hej {lead_company},

{relevance_sentence}

Jag heter {sender_name} och representerar {sender_company}. Vi arbetar med {offer} för {target_customer}.{proof_line}

{improved_message}

Är ni öppna för att jag skickar mer information eller bokar in ett kort samtal?

Med vänliga hälsningar
{sender_name}
{sender_company}{contact_lines}
"""

    return subject, body


def create_subject(lead_obj, profile):
    company = clean(lead_obj.company_name, "ert företag")
    angle = build_pitch_angle(lead_obj, profile)

    if angle:
        return f"Snabb fråga om {angle}"

    return f"Snabb fråga till {company}"


def create_pitch_for_many(leads, profile=None, custom_message=None):
    results = []

    for lead in leads:
        subject, body = create_pitch_for_lead(
            lead=lead,
            profile=profile,
            custom_message=custom_message,
        )

        results.append({
            "lead": lead,
            "subject": subject,
            "body": body,
        })

    return results


def build_contact_lines(phone, website):
    lines = ""

    if phone:
        lines += f"\nTelefon: {phone}"

    if website:
        lines += f"\nHemsida: {website}"

    return lines


def improve_custom_message(
    message,
    lead_company,
    lead_industry,
    lead_city,
    sender_company,
    offer,
    target_customer,
):
    message = clean(message)

    if not message:
        return (
            f"Jag tror att {sender_company} kan vara relevant för {lead_company}, "
            f"eftersom vi arbetar med {offer} för {target_customer}."
        )

    replacements = {
        "[företag]": lead_company,
        "{företag}": lead_company,
        "[company]": lead_company,
        "{company}": lead_company,
        "[lead_company]": lead_company,
        "{lead_company}": lead_company,
        "[bransch]": lead_industry,
        "{bransch}": lead_industry,
        "[stad]": lead_city,
        "{stad}": lead_city,
        "[mitt företag]": sender_company,
        "{mitt företag}": sender_company,
        "[sender_company]": sender_company,
        "{sender_company}": sender_company,
        "[erbjudande]": offer,
        "{erbjudande}": offer,
        "[offer]": offer,
        "{offer}": offer,
        "[målgrupp]": target_customer,
        "{målgrupp}": target_customer,
    }

    for old, new in replacements.items():
        message = message.replace(old, new)

    return polish_custom_message(message)


def polish_custom_message(message):
    message = clean(message)

    if not message:
        return ""

    message = message.replace("  ", " ")

    if not message.endswith((".", "?", "!")):
        message += "."

    return message