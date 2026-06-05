from datetime import datetime, timedelta
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

CONFIG_FILE = "google_calendar_config.json"
TOKEN_FILE = "calendar_token.json"


def get_calendar_service():

    creds = None

    if os.path.exists(TOKEN_FILE):

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                CONFIG_FILE,
                SCOPES
            )

            creds = flow.run_local_server(
                port=8080
            )

        with open(TOKEN_FILE, "w") as token:

            token.write(
                creds.to_json()
            )

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


def get_events_for_day(day_offset=0):

    service = get_calendar_service()

    day = datetime.now() + timedelta(days=day_offset)

    start = day.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    ).isoformat() + "Z"

    end = day.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=0
    ).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if not events:

        if day_offset == 0:
            return "Du har inget idag bror."

        if day_offset == 1:
            return "Du har inget imorgon bror."

        return "Tomt bror."

    lines = []

    for event in events[:5]:

        title = event.get(
            "summary",
            "Utan titel"
        )

        start_time = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        try:

            hour = datetime.fromisoformat(
                start_time.replace("Z", "+00:00")
            ).strftime("%H:%M")

            lines.append(
                f"{hour} {title}"
            )

        except:

            lines.append(title)

    return "Du har: " + ", ".join(lines)


def add_calendar_event(text):

    service = get_calendar_service()

    lower = text.lower()

    day_offset = 0

    if "imorgon" in lower:
        day_offset = 1

    match = re.search(
        r"(\\d{1,2})([:.](\\d{2}))?",
        lower
    )

    if match:

        hour = int(match.group(1))
        minute = int(match.group(3) or 0)

    else:

        hour = 12
        minute = 0

    title = text

    remove_words = [
        "lägg till",
        "skapa",
        "boka",
        "möte",
        "i kalendern",
        "kalender",
        "imorgon",
        "idag"
    ]

    for word in remove_words:
        title = title.replace(word, "")

    title = re.sub(
        r"\\d{1,2}([:.]\\d{2})?",
        "",
        title
    ).strip()

    if not title:
        title = "Möte"

    start = datetime.now() + timedelta(days=day_offset)

    start = start.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    end = start + timedelta(hours=1)

    event = {
        "summary": title,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "Europe/Stockholm"
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "Europe/Stockholm"
        }
    }

    service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return f"Klart bror, la in {title} {start.strftime('%H:%M')}."