import os

folders = [
    "agents",
    "content_factory/scripts",
    "content_factory/voice",
    "content_factory/assets",
    "ready_to_post"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

script_agent = r'''
import random

def make_script(trend):
    source = trend.get("source_title", "a viral business idea")

    hooks = [
        "Bro, this business idea is actually genius.",
        "Nobody talks about this lazy business idea.",
        "This is how a teenager could make money with AI.",
        "This side hustle is boring... but it works.",
        "If I had to start from zero, I would do this."
    ]

    ideas = [
        "Find local businesses with terrible websites, remake them with AI, and charge 300 dollars.",
        "Make short form videos for local restaurants using AI captions and simple edits.",
        "Find real estate agents with bad social media and sell them 30 days of content.",
        "Build landing pages for small gyms, barbers, and cleaners using AI tools.",
        "Create AI product videos for small ecommerce stores and charge per video."
    ]

    hook = random.choice(hooks)
    business = random.choice(ideas)

    script_lines = [
        hook,
        business,
        "Step one, find a boring business with bad marketing.",
        "Step two, make their content or website look ten times better.",
        "Step three, send them a simple before and after.",
        "Most people chase fancy ideas.",
        "Smart people solve boring problems and get paid.",
        "Follow for more business ideas."
    ]

    title = "This business idea is actually genius #Shorts"

    description = "#business #startup #sidehustle #money #ai #entrepreneur #shorts"

    return title, script_lines, description
'''

trend_agent = r'''
import random
import yt_dlp

SEARCHES = [
    "viral AI business ideas shorts",
    "side hustle ideas shorts",
    "make money with AI shorts",
    "startup ideas shorts",
    "boring business ideas shorts",
    "AI agency business shorts"
]

FALLBACK = [
    "AI content agency business idea",
    "local business website side hustle",
    "short form content agency idea",
    "AI automation agency idea",
    "boring business that makes money"
]

def get_viral_idea():
    query = random.choice(SEARCHES)

    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "default_search": "ytsearch15"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(query, download=False)

        titles = []
        for item in data.get("entries", []):
            title = item.get("title")
            if title:
                titles.append(title)

        if titles:
            title = random.choice(titles)
            return {
                "source_title": title,
                "idea": "Use the format inspiration only, create an original business explanation."
            }

    except Exception as e:
        print("Trend fallback:", e)

    idea = random.choice(FALLBACK)
    return {
        "source_title": idea,
        "idea": idea
    }
'''

voice_agent = r'''
import os
import subprocess
import sys
from datetime import datetime

def make_voice(script_lines):
    os.makedirs("content_factory/voice", exist_ok=True)

    text = " ".join(script_lines)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    voice_path = f"content_factory/voice/voice_{timestamp}.mp3"

    cmd = [
        sys.executable,
        "-m",
        "edge_tts",
        "--voice",
        "en-US-GuyNeural",
        "--rate",
        "+12%",
        "--text",
        text,
        "--write-media",
        voice_path
    ]

    subprocess.run(cmd, check=True)
    return voice_path
'''

character_agent = r'''
import os
from PIL import Image, ImageDraw

def create_character_image():
    os.makedirs("content_factory/assets", exist_ok=True)
    path = "content_factory/assets/cartoon_business_guy.png"

    img = Image.new("RGB", (1080, 1920), (18, 20, 28))
    d = ImageDraw.Draw(img)

    # Background
    d.rectangle([0, 0, 1080, 1920], fill=(18, 20, 28))
    d.ellipse([-250, 200, 500, 950], fill=(35, 40, 70))
    d.ellipse([650, 900, 1350, 1650], fill=(45, 35, 75))

    # Desk
    d.rectangle([0, 1450, 1080, 1920], fill=(38, 32, 30))

    # Body
    d.rounded_rectangle([330, 980, 750, 1540], radius=70, fill=(45, 90, 160))
    d.polygon([(330, 980), (540, 1320), (750, 980)], fill=(235, 235, 235))
    d.polygon([(500, 1180), (580, 1180), (555, 1420), (525, 1420)], fill=(210, 40, 60))

    # Neck
    d.rounded_rectangle([470, 850, 610, 1030], radius=45, fill=(245, 185, 135))

    # Head
    d.ellipse([310, 470, 770, 940], fill=(250, 195, 145))

    # Ears
    d.ellipse([270, 650, 350, 780], fill=(245, 185, 135))
    d.ellipse([730, 650, 810, 780], fill=(245, 185, 135))

    # Hair
    d.pieslice([310, 420, 770, 780], 180, 360, fill=(60, 35, 25))
    d.rectangle([340, 470, 740, 620], fill=(60, 35, 25))

    # Eyes
    d.ellipse([420, 655, 500, 735], fill=(255, 255, 255))
    d.ellipse([580, 655, 660, 735], fill=(255, 255, 255))
    d.ellipse([455, 685, 485, 715], fill=(0, 0, 0))
    d.ellipse([615, 685, 645, 715], fill=(0, 0, 0))

    # Nose
    d.rounded_rectangle([520, 710, 570, 805], radius=20, fill=(235, 165, 120))

    # Mouth
    d.arc([440, 790, 650, 900], 10, 170, fill=(80, 20, 20), width=10)

    # Eyebrows
    d.line([400, 620, 510, 645], fill=(45, 25, 20), width=12)
    d.line([570, 645, 680, 620], fill=(45, 25, 20), width=12)

    # Hands
    d.ellipse([230, 1320, 390, 1480], fill=(245, 185, 135))
    d.ellipse([690, 1320, 850, 1480], fill=(245, 185, 135))

    # Laptop
    d.rounded_rectangle([280, 1280, 800, 1600], radius=35, fill=(85, 90, 100))
    d.rounded_rectangle([330, 1330, 750, 1540], radius=20, fill=(20, 25, 35))
    d.text((445, 1425), "AI BIZ", fill=(255, 255, 255))

    img.save(path)
    return path
'''

video_agent = r'''
import os
import subprocess
from datetime import datetime

FONT = "C\\:/Windows/Fonts/arial.ttf"

def clean(text):
    bad = ["'", '"', ":", "\\", "|", "{", "}", "[", "]"]
    for b in bad:
        text = text.replace(b, "")
    return text

def audio_duration(audio_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    return float(subprocess.check_output(cmd).decode().strip())

def make_video(script_lines, voice_path, character_path):
    os.makedirs("ready_to_post", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = f"ready_to_post/cartoon_business_{timestamp}.mp4"

    duration = max(18, audio_duration(voice_path) + 1)
    segment = duration / len(script_lines)

    filters = []

    # subtle zoom/pulse
    filters.append(
        "[0:v]scale=1080:1920,zoompan=z='1+0.018*sin(on/12)':"
        "d=1:s=1080x1920:fps=30[bg]"
    )

    last = "[bg]"

    for i, line in enumerate(script_lines):
        start = i * segment
        end = (i + 1) * segment
        text = clean(line).upper()

        out = f"[v{i}]"
        filters.append(
            f"{last}drawtext=fontfile='{FONT}':"
            f"text='{text}':"
            "fontcolor=white:"
            "fontsize=58:"
            "x=(w-text_w)/2:"
            "y=220:"
            "box=1:"
            "boxcolor=black@0.75:"
            "boxborderw=28:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
            f"{out}"
        )
        last = out

    filter_complex = ";".join(filters)

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", character_path,
        "-i", voice_path,
        "-filter_complex", filter_complex,
        "-map", last,
        "-map", "1:a",
        "-t", str(duration),
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        video_path
    ]

    subprocess.run(cmd, check=True)
    return video_path
'''

youtube_agent = r'''
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

def upload_short(video_path, title, description, privacy="public"):
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["shorts", "business", "ai", "startup", "sidehustle"],
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
    print("Uploaded:", "https://youtube.com/shorts/" + video_id)
    return video_id
'''

runner = r'''
from agents.trend_agent import get_viral_idea
from agents.script_agent import make_script
from agents.voice_agent import make_voice
from agents.character_agent import create_character_image
from agents.video_agent import make_video
from agents.youtube_upload_agent import upload_short

trend = get_viral_idea()
print("Trend inspiration:", trend["source_title"])

title, script_lines, description = make_script(trend)

print("Creating character...")
character_path = create_character_image()

print("Creating English voice...")
voice_path = make_voice(script_lines)

print("Creating cartoon business video...")
video_path = make_video(script_lines, voice_path, character_path)

print("Uploading to YouTube Shorts...")
upload_short(
    video_path=video_path,
    title=title,
    description=description,
    privacy="public"
)

print("Done.")
'''

with open("agents/script_agent.py", "w", encoding="utf-8") as f:
    f.write(script_agent.strip())

with open("agents/trend_agent.py", "w", encoding="utf-8") as f:
    f.write(trend_agent.strip())

with open("agents/voice_agent.py", "w", encoding="utf-8") as f:
    f.write(voice_agent.strip())

with open("agents/character_agent.py", "w", encoding="utf-8") as f:
    f.write(character_agent.strip())

with open("agents/video_agent.py", "w", encoding="utf-8") as f:
    f.write(video_agent.strip())

with open("agents/youtube_upload_agent.py", "w", encoding="utf-8") as f:
    f.write(youtube_agent.strip())

with open("run_cartoon_business_short.py", "w", encoding="utf-8") as f:
    f.write(runner.strip())

print("Klart.")
print("Kör nu:")
print("python run_cartoon_business_short.py")