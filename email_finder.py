import re
import requests
from urllib.parse import urljoin


EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def clean_email(email):
    bad_extensions = [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"]
    email = email.strip().lower()

    if any(email.endswith(ext) for ext in bad_extensions):
        return None

    if "example" in email or "test@" in email:
        return None

    return email


def extract_emails(html):
    found = set()

    for email in EMAIL_RE.findall(html or ""):
        cleaned = clean_email(email)
        if cleaned:
            found.add(cleaned)

    return list(found)


def fetch_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 FlerKunderLeadBot/1.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    return response.text


def find_email_from_website(website):
    if not website:
        return None

    if not website.startswith("http"):
        website = "https://" + website

    pages_to_check = [
        website,
        urljoin(website, "/kontakt"),
        urljoin(website, "/contact"),
        urljoin(website, "/kontakta-oss"),
        urljoin(website, "/om-oss"),
    ]

    for page in pages_to_check:
        try:
            html = fetch_url(page)
            emails = extract_emails(html)

            if emails:
                return emails[0]

        except Exception as e:
            print("Email finder failed for", page, e)

    return None