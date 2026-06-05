import os

folders = [
    "agents",
    "ready_to_post"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

youtube_agent_code = r'''
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "youtube_token.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(
                    "client_secret.json saknas. Lägg den i din JARVIS-mapp."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def upload_short(video_path, title, description, privacy="public"):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Videon finns inte: {video_path}")

    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description + "\n\n#Shorts",
            "tags": ["shorts", "ai", "jarvis"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = request.execute()
    video_id = response.get("id")

    print("Uppladdad video ID:", video_id)
    print("Länk: https://youtube.com/shorts/" + video_id)

    return video_id
'''

test_code = r'''
from agents.youtube_upload_agent import upload_short

upload_short(
    video_path="ready_to_post/test.mp4",
    title="Test Short från Jarvis #Shorts",
    description="Detta är ett automatiskt test från min Jarvis AI.",
    privacy="private"
)
'''

init_code = ""

with open("agents/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_code)

with open("agents/youtube_upload_agent.py", "w", encoding="utf-8") as f:
    f.write(youtube_agent_code.strip())

with open("test_youtube_upload.py", "w", encoding="utf-8") as f:
    f.write(test_code.strip())

print("Klart!")
print("Skapade:")
print("- agents/youtube_upload_agent.py")
print("- agents/__init__.py")
print("- ready_to_post/")
print("- test_youtube_upload.py")
print("")
print("Nästa steg:")
print("1. Lägg client_secret.json i JARVIS-mappen.")
print("2. Lägg en video som heter test.mp4 i ready_to_post-mappen.")
print("3. Kör: python test_youtube_upload.py")