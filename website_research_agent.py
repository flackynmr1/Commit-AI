import re
import requests
from bs4 import BeautifulSoup


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
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=8
        )

        if response.status_code >= 400:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(" ")
        text = clean_text(text)

        return text[:max_chars]

    except Exception:
        return ""


def analyze_lead_relevance(lead, profile):
    company = getattr(lead, "company_name", "företaget")
    industry = getattr(lead, "industry", "")
    city = getattr(lead, "city", "")
    website = getattr(lead, "website", "")

    offer = profile.get("offer", "")
    target_customer = profile.get("target_customer", "")
    sender_company = profile.get("company_name", "")

    website_text = fetch_website_text(website)

    return build_research_summary(
        company=company,
        industry=industry,
        city=city,
        website_text=website_text,
        offer=offer,
        target_customer=target_customer,
        sender_company=sender_company,
    )


def build_research_summary(
    company,
    industry,
    city,
    website_text,
    offer,
    target_customer,
    sender_company,
):
    text = website_text.lower()

    findings = []

    if "akut" in text:
        findings.append("de verkar erbjuda akuta tjänster där snabba förfrågningar kan vara viktiga")

    if "offert" in text:
        findings.append("de verkar ta emot offertförfrågningar via hemsidan")

    if "fastighet" in text or "bostadsrätt" in text or "brf" in text:
        findings.append("de verkar arbeta mot fastigheter eller bostadsrättsföreningar")

    if "företag" in text or "b2b" in text:
        findings.append("de verkar rikta sig mot företagskunder")

    if "privat" in text:
        findings.append("de verkar även arbeta mot privatpersoner")

    if not findings:
        findings.append(
            f"de är ett företag inom {industry} i {city}, vilket kan vara relevant om de vill få fler kundförfrågningar"
        )

    if "hemsida" in offer.lower() or "webb" in offer.lower():
        angle = (
            "en tydligare hemsida kan hjälpa dem få fler förfrågningar, "
            "särskilt från kunder som söker lokalt"
        )
    elif "marknadsföring" in offer.lower() or "leads" in offer.lower():
        angle = (
            "ett bättre leadflöde kan hjälpa dem få fler relevanta kundförfrågningar"
        )
    else:
        angle = (
            f"{offer} kan vara relevant om de vill förbättra sitt kundflöde eller sin service"
        )

    return {
        "company": company,
        "findings": findings,
        "angle": angle,
        "website_found": bool(website_text),
    }