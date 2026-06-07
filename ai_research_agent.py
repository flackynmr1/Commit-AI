import os
import re
import requests
from bs4 import BeautifulSoup


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_website_text(url, max_chars=5000):
    if not url:
        return ""

    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )

        if response.status_code >= 400:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return clean_text(soup.get_text(" "))[:max_chars]

    except Exception:
        return ""


def create_ai_research_pitch(lead, profile):
    website_text = fetch_website_text(getattr(lead, "website", ""))

    lead_company = getattr(lead, "company_name", "företaget")
    lead_industry = getattr(lead, "industry", "")
    lead_city = getattr(lead, "city", "")

    sender_name = profile.get("sender_name", "Ditt namn")
    sender_company = profile.get("company_name", "Ditt företag")
    offer = profile.get("offer", "våra tjänster")
    target_customer = profile.get("target_customer", "företag")
    proof = profile.get("proof", "")
    phone = profile.get("phone", "")
    website = profile.get("website", "")

    if not GEMINI_API_KEY or not website_text:
        from email_agent import create_pitch_for_lead
        return create_pitch_for_lead(lead, profile)

    prompt = f"""
Du är en expert på B2B cold email på svenska.

MITT FÖRETAG:
Namn: {sender_company}
Kontaktperson: {sender_name}
Erbjudande: {offer}
Målgrupp: {target_customer}
Bevis/case: {proof}

LEAD:
Företag: {lead_company}
Bransch: {lead_industry}
Stad: {lead_city}

TEXT FRÅN LEADETS HEMSIDA:
{website_text}

Skriv ett kort personligt mail på svenska.

Krav:
- Max 130 ord
- Låt naturligt och mänskligt
- Förklara konkret varför mitt erbjudande är relevant för just detta företag
- Säg inte "jag såg att ni arbetar inom..." om det låter generiskt
- Undvik fluff
- Sälj mitt företag, inte FlerKunder
- Avsluta med enkel fråga om kort samtal eller att skicka mer info

Returnera exakt:
SUBJECT: ...
BODY: ...
"""

    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-1.5-flash:generateContent"
            f"?key={GEMINI_API_KEY}"
        )

        res = requests.post(
            url,
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            },
            timeout=20,
        )

        data = res.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        subject = "Snabb fråga"
        body = text

        if "SUBJECT:" in text and "BODY:" in text:
            subject = text.split("SUBJECT:", 1)[1].split("BODY:", 1)[0].strip()
            body = text.split("BODY:", 1)[1].strip()

        contact = ""
        if phone:
            contact += f"\nTelefon: {phone}"
        if website:
            contact += f"\nHemsida: {website}"

        if contact and contact not in body:
            body += f"\n\nMed vänliga hälsningar\n{sender_name}\n{sender_company}{contact}"

        return subject, body

    except Exception:
        from email_agent import create_pitch_for_lead
        return create_pitch_for_lead(lead, profile)