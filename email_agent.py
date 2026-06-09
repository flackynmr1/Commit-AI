from relevance_engine import analyze_lead, clean, fix_text, build_ai_profile


def get_attr(obj, name, fallback=""):
    return getattr(obj, name, fallback) or fallback


def ensure_profile(profile):
    profile = profile or {}
    if "service_type" not in profile:
        return build_ai_profile(profile)
    return profile


def describe_offer(profile):
    service_type = clean(profile.get("service_type", "other"))
    offer = fix_text(profile.get("offer", ""))
    problem = fix_text(profile.get("problem_solved", ""))
    result = fix_text(profile.get("customer_result", ""))
    target = fix_text(profile.get("target_customer", ""))

    if service_type == "website":
        return f"bygga tydligare och mer förtroendeingivande hemsidor för {target or 'lokala företag'}"
    if service_type == "seo":
        return f"hjälpa {target or 'företag'} att synas bättre på Google och få fler relevanta besökare"
    if service_type == "ads":
        return f"hjälpa {target or 'företag'} att få fler kunder genom annonsering"
    if service_type == "ai_chatbot":
        return f"hjälpa {target or 'företag'} att svara snabbare på kunder och samla in fler förfrågningar"
    if service_type == "vvs":
        return offer or "hjälpa företag med VVS-installationer och projektstöd"

    if offer:
        return offer
    return f"hjälpa {target or 'företag'} med {result or 'bättre kundflöde'}"


def create_pitch_for_lead(lead, profile=None, custom_message=None):
    profile = ensure_profile(profile)

    lead_company = clean(get_attr(lead, "company_name", "ert företag"))
    sender_name = clean(profile.get("sender_name"), "Elias")
    sender_company = clean(profile.get("company_name"), "FlerKunder")
    proof = clean(profile.get("proof", ""))
    phone = clean(profile.get("phone", ""))
    website = clean(profile.get("website", ""))

    analysis = analyze_lead(lead, profile)
    offer_sentence = describe_offer(profile)

    subject = f"En idé för {lead_company}"

    contact_line = ""
    if phone:
        contact_line += f"\nTelefon: {phone}"
    if website:
        contact_line += f"\nHemsida: {website}"

    proof_line = f"\n\nKort bakgrund: {proof}" if proof else ""

    if not analysis["is_relevant"]:
        body = f"""Hej {lead_company},

{analysis["insight"]}

Jag vill vara transparent: jag är inte helt säker på att det här är en perfekt matchning, eftersom {analysis["warnings"][0] if analysis["warnings"] else "kopplingen mellan våra verksamheter inte är helt självklar"}.

Vi på {sender_company} arbetar med att {offer_sentence}. Om ni någon gång har behov av detta, eller samarbetar med företag där det kan vara relevant, tar jag gärna en kort kontakt.{proof_line}

Är det okej om jag skickar lite mer information?

Vänliga hälsningar,
{sender_name}
{sender_company}{contact_line}
"""
        return subject, body.strip()

    body = f"""Hej {lead_company},

{analysis["insight"]}

I er bransch är det ofta viktigt att {analysis["problem"]}. Därför tror jag att det kan finnas en relevant möjlighet kopplat till {analysis["angle"]}.

Vi på {sender_company} arbetar med att {offer_sentence}. För ett företag som ert kan det framför allt hjälpa med att {analysis["value"]}.{proof_line}

Vill du att jag skickar ett kort exempel på hur det skulle kunna se ut för er?

Vänliga hälsningar,
{sender_name}
{sender_company}{contact_line}
"""

    return subject, body.strip()


def create_pitch_for_many(leads, profile=None, custom_message=None):
    results = []
    for lead in leads:
        subject, body = create_pitch_for_lead(lead, profile, custom_message)
        results.append((lead, subject, body))
    return results
