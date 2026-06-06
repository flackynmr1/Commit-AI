import base64
import os
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GMAIL_CLIENT_ID"),
                "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GMAIL_REDIRECT_URI")],
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv("GMAIL_REDIRECT_URI"),
        autogenerate_code_verifier=False,
    )


def create_gmail_draft(token_data, to_email, subject, body):
    creds = Credentials(**token_data)
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()

    return draft