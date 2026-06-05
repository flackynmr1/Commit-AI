from datetime import datetime, timedelta
from urllib.parse import quote


def create_google_calendar_link(company_name):
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(minutes=30)

    start_str = start.strftime("%Y%m%dT%H%M%SZ")
    end_str = end.strftime("%Y%m%dT%H%M%SZ")

    title = quote(f"Demo med {company_name}")
    details = quote(
        "Kort demo av LeadBot AI och hur en AI-chatbot kan samla fler leads."
    )
    location = quote("Google Meet / Telefon")

    return (
        "https://calendar.google.com/calendar/render"
        f"?action=TEMPLATE&text={title}"
        f"&dates={start_str}/{end_str}"
        f"&details={details}"
        f"&location={location}"
    )