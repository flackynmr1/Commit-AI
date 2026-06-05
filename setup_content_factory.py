import os

folders = [
    "agents",
    "ready_to_post",
    "content_factory/scripts",
    "content_factory/videos"
]

for f in folders:
    os.makedirs(f, exist_ok=True)

main_code = r'''
from agents.content_factory_agent import create_ai_short
from agents.youtube_upload_agent import upload_short

video_path, title, description = create_ai_short()

upload_short(
    video_path=video_path,
    title=title,
    description=description,
    privacy="private"
)

print("Klar! Video skapad och uppladdad.")
'''

content_factory_code = r'''
import os
import random
import subprocess
from datetime import datetime

IDEAS = [
    "3 sjuka AI-saker som folk inte fattar händer just nu",
    "Så här kan AI förändra hur vi tjänar pengar online",
    "5 misstag nästan alla gör när de försöker växa på TikTok",
    "Den här enkla vanan kan göra dig mer produktiv",
    "Så bygger du ett automatiskt system som jobbar åt dig"
]

def create_ai_short():
    idea = random.choice(IDEAS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    title = idea[:90] + " #Shorts"
    description = f"{idea}\n\nSkapad automatiskt av Jarvis AI.\n#ai #shorts #automation"

    script = f"""
    Visste du detta?
    {idea}.
    De flesta väntar på rätt tillfälle.
    Men vinnarna bygger system som jobbar varje dag.
    Följ för fler AI och automation tips.
    """

    script_path = f"content_factory/scripts/script_{timestamp}.txt"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    video_path = f"ready_to_post/short_{timestamp}.mp4"

    text = script.replace("\n", " ").replace("'", "")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920:d=18",
        "-vf",
        f"drawtext=text='{text}':fontcolor=white:fontsize=58:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5:boxborderw=20",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        video_path
    ]

    subprocess.run(cmd, check=True)

    return video_path, title, description
'''

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
                raise FileNotFoundError("client_secret.json saknas i JARVIS-mappen.")

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def upload_short(video_path, title, description, privacy="private"):
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description + "\n\n#Shorts",
            "tags": ["shorts", "ai", "automation", "jarvis"],
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

    print("Uppladdad:", "https://youtube.com/shorts/" + video_id)
    return video_id
'''

with open("agents/__init__.py", "w", encoding="utf-8") as f:
    f.write("")

with open("agents/content_factory_agent.py", "w", encoding="utf-8") as f:
    f.write(content_factory_code.strip())

with open("agents/youtube_upload_agent.py", "w", encoding="utf-8") as f:
    f.write(youtube_agent_code.strip())

with open("run_ai_short.py", "w", encoding="utf-8") as f:
    f.write(main_code.strip())

print("Klart! Nu har Jarvis AI-video + YouTube upload.")
print("Kör nu: python run_ai_short.py")