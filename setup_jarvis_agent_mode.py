import os
import shutil

folders = [
    "agents",
    "content_factory/logs",
    "content_factory/scripts",
    "content_factory/voice",
    "content_factory/assets/mockups",
    "content_factory/temp",
    "ready_to_post"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Backup main.py
if os.path.exists("main.py"):
    shutil.copy("main.py", "main_backup_before_agents.py")

autonomous_manager = r'''
import os
import json
import time
from datetime import datetime

from agents.trend_agent import get_viral_idea
from agents.script_agent import make_script
from agents.voice_agent import make_voice
from agents.visual_asset_agent import make_assets
from agents.character_agent import create_character_image
from agents.video_agent import make_video

TASK_FILE = "content_factory/logs/tasks.json"
STATUS_FILE = "content_factory/logs/status.json"

AGENTS = [
    "Trend Agent",
    "Script Agent",
    "Visual Agent",
    "Voice Agent",
    "Character Agent",
    "Video Agent",
    "Analytics Agent",
    "Learning Agent"
]

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_tasks():
    if os.path.exists(TASK_FILE):
        try:
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def log(agent, status, detail):
    tasks = load_tasks()
    item = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "status": status,
        "detail": detail
    }
    tasks.append(item)
    save_json(TASK_FILE, tasks[-80:])
    print(f"[{item['time']}] {agent}: {status} - {detail}")

def set_status(mode, created=0, running=False):
    save_json(STATUS_FILE, {
        "mode": mode,
        "created_videos": created,
        "running": running,
        "updated": datetime.now().strftime("%H:%M:%S")
    })

def open_videos_folder():
    path = os.path.abspath("ready_to_post")
    os.startfile(path)

def start_yt_shorts_factory(amount=5, upload=False):
    save_json(TASK_FILE, [])
    set_status("Starting agents", 0, True)

    log("Jarvis", "STARTING", "Agent mode activated")

    for agent in AGENTS:
        log(agent, "ONLINE", "Agent initialized")
        time.sleep(0.15)

    created_videos = []

    for n in range(1, amount + 1):
        set_status(f"Creating video {n}/{amount}", len(created_videos), True)
        log("Jarvis", "MISSION", f"Creating video {n}/{amount}")

        trend = get_viral_idea()
        log("Trend Agent", "DONE", trend.get("source_title", "Trend selected"))

        title, script_lines, description = make_script(trend)
        log("Script Agent", "DONE", title)

        scene_paths = make_assets(script_lines)
        log("Visual Agent", "DONE", f"{len(scene_paths)} mockups created")

        voice_paths = make_voice(script_lines)
        log("Voice Agent", "DONE", f"{len(voice_paths)} voice parts created")

        character_path = create_character_image()
        log("Character Agent", "DONE", "Character layout created")

        video_path = make_video(script_lines, voice_paths, character_path, scene_paths)
        created_videos.append(video_path)
        log("Video Agent", "DONE", video_path)

        if upload:
            try:
                from agents.youtube_upload_agent import upload_short
                upload_short(video_path, title, description, privacy="public")
                log("Upload Agent", "DONE", "Uploaded to YouTube Shorts")
            except Exception as e:
                log("Upload Agent", "FAILED", str(e))
        else:
            log("Upload Agent", "SKIPPED", "Upload disabled for testing")

    log("Analytics Agent", "READY", "Analytics connection next step")
    log("Learning Agent", "READY", "Will learn from views later")
    log("Jarvis", "FINISHED", f"Created {len(created_videos)} videos")

    set_status("Finished", len(created_videos), False)
    return created_videos
'''

trend_agent = r'''
import random

IDEAS = [
    "local business website redesign side hustle",
    "AI content agency for restaurants",
    "short form content agency for real estate agents",
    "AI landing page business",
    "boring business that makes money",
    "small business automation service",
    "AI product video agency",
    "website before and after business idea"
]

def get_viral_idea():
    idea = random.choice(IDEAS)
    return {
        "source_title": idea,
        "idea": idea
    }
'''

script_agent = r'''
import random

def make_script(trend):
    hooks = [
        "Bro, this business idea is actually genius.",
        "Nobody talks about this boring business idea.",
        "If I had to start from zero, I would do this.",
        "This is not sexy, but it can make money.",
        "Here is a simple AI business idea."
    ]

    businesses = [
        "Find local businesses with terrible websites, remake them with AI, and charge three hundred dollars.",
        "Find restaurants with weak social media, make them short videos, and sell a monthly content package.",
        "Find real estate agents with boring posts, create thirty days of content, and charge a setup fee.",
        "Find barbers, gyms, and cleaners with no landing page, build one fast, and sell the upgrade.",
        "Create before and after product videos for small online stores, then charge per video."
    ]

    hook = random.choice(hooks)
    business = random.choice(businesses)

    script_lines = [
        hook,
        business,
        "Step one, find a boring business with bad marketing.",
        "Step two, make their website or content look ten times better.",
        "Step three, send them a simple before and after.",
        "Most people chase fancy ideas.",
        "Smart people solve boring problems and get paid.",
        "Follow for more business ideas."
    ]

    title = "This business idea is actually genius #Shorts"
    description = "#business #startup #sidehustle #money #ai #entrepreneur #shorts"

    return title, script_lines, description
'''

voice_agent = r'''
import os
import subprocess
import sys
from datetime import datetime

def make_voice(script_lines):
    os.makedirs("content_factory/voice", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    voice_paths = []

    for i, line in enumerate(script_lines, start=1):
        voice_path = f"content_factory/voice/scene_{timestamp}_{i}.mp3"

        cmd = [
            sys.executable,
            "-m",
            "edge_tts",
            "--voice",
            "en-US-GuyNeural",
            "--rate",
            "+12%",
            "--text",
            line,
            "--write-media",
            voice_path
        ]

        subprocess.run(cmd, check=True)
        voice_paths.append(voice_path)

    return voice_paths
'''

character_agent = r'''
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BOLD = "C:/Windows/Fonts/arialbd.ttf"
REG = "C:/Windows/Fonts/arial.ttf"

def create_character_image():
    os.makedirs("content_factory/assets", exist_ok=True)
    path = "content_factory/assets/cartoon_business_guy.png"

    img = Image.new("RGB", (W, H), (18, 20, 28))
    d = ImageDraw.Draw(img)

    d.ellipse([-280, 120, 480, 880], fill=(32, 40, 78))
    d.ellipse([690, 950, 1400, 1700], fill=(45, 35, 82))

    # Big UI screen frame
    d.rounded_rectangle([120, 520, 960, 1220], radius=48, fill=(5, 7, 12), outline=(255,255,255), width=8)
    d.rectangle([150, 550, 930, 610], fill=(25, 28, 42))

    # Character bottom-right
    d.ellipse([610, 1120, 910, 1420], fill=(245, 190, 140))
    d.rectangle([675, 1400, 845, 1700], fill=(45, 90, 160))
    d.ellipse([675, 1220, 725, 1270], fill=(255,255,255))
    d.ellipse([795, 1220, 845, 1270], fill=(255,255,255))
    d.ellipse([695, 1238, 718, 1260], fill=(0,0,0))
    d.ellipse([815, 1238, 838, 1260], fill=(0,0,0))
    d.arc([700, 1300, 830, 1370], 10, 170, fill=(80,20,20), width=8)

    # Desk
    d.rectangle([0, 1640, 1080, 1920], fill=(34, 28, 26))

    try:
        f = ImageFont.truetype(BOLD, 46)
        d.text((165, 555), "BUSINESS IDEA", font=f, fill=(255,255,255))
    except:
        pass

    img.save(path)
    return path
'''

scene_planner = r'''
def plan_scenes(script_lines):
    scenes = []

    for line in script_lines:
        t = line.lower()

        if "website" in t or "landing page" in t or "redesign" in t:
            scenes.append({"type": "website_before_after", "line": line})
        elif "ai" in t or "automation" in t:
            scenes.append({"type": "ai_dashboard", "line": line})
        elif "send" in t or "client" in t or "owner" in t:
            scenes.append({"type": "client_email", "line": line})
        elif "charge" in t or "paid" in t or "money" in t or "dollars" in t:
            scenes.append({"type": "payment", "line": line})
        elif "social media" in t or "content" in t or "videos" in t or "posts" in t:
            scenes.append({"type": "content_calendar", "line": line})
        elif "problem" in t or "boring" in t or "bad marketing" in t:
            scenes.append({"type": "problem_list", "line": line})
        else:
            scenes.append({"type": "business_laptop", "line": line})

    return scenes
'''

visual_asset_agent = r'''
import os
from PIL import Image, ImageDraw, ImageFont
from agents.scene_planner_agent import plan_scenes

W, H = 760, 560
BOLD = "C:/Windows/Fonts/arialbd.ttf"
REG = "C:/Windows/Fonts/arial.ttf"

def f(path, size):
    return ImageFont.truetype(path, size)

def base():
    img = Image.new("RGB", (W, H), (10, 12, 22))
    d = ImageDraw.Draw(img)
    d.ellipse([-140, -120, 340, 360], fill=(30, 42, 90))
    d.ellipse([420, 220, 920, 720], fill=(42, 28, 80))
    return img, d

def save(img, i):
    os.makedirs("content_factory/assets/mockups", exist_ok=True)
    path = f"content_factory/assets/mockups/scene_{i}.jpg"
    img.save(path, quality=94)
    return path

def website_before_after(i):
    img, d = base()
    d.text((165, 25), "BEFORE  →  AFTER", font=f(BOLD, 42), fill=(255,255,255))

    d.rounded_rectangle([45, 105, 350, 445], radius=24, fill=(235,235,235))
    d.rectangle([75, 140, 320, 190], fill=(185,45,45))
    d.rectangle([75, 225, 310, 260], fill=(180,180,180))
    d.rectangle([75, 295, 270, 395], fill=(160,160,160))
    d.text((110, 465), "OLD SITE", font=f(BOLD, 28), fill=(255,255,255))

    d.rounded_rectangle([410, 105, 715, 445], radius=24, fill=(13,20,38))
    d.rounded_rectangle([445, 145, 680, 230], radius=18, fill=(75,120,255))
    d.rounded_rectangle([445, 280, 555, 395], radius=16, fill=(255,255,255))
    d.rounded_rectangle([575, 280, 680, 395], radius=16, fill=(60,220,150))
    d.text((465, 465), "NEW SITE", font=f(BOLD, 28), fill=(255,255,255))
    return save(img, i)

def ai_dashboard(i):
    img, d = base()
    d.text((210, 25), "AI BUILDS IT", font=f(BOLD, 46), fill=(255,255,255))
    d.rounded_rectangle([70, 115, 690, 455], radius=30, fill=(8,10,20), outline=(95,130,255), width=6)

    for y in [165, 225, 285, 345]:
        d.rounded_rectangle([120, y, 640, y+36], radius=12, fill=(35,45,80))
        d.rectangle([145, y+13, 335, y+22], fill=(120,170,255))
        d.rectangle([370, y+13, 610, y+22], fill=(80,220,150))

    d.ellipse([320, 385, 440, 505], fill=(75,120,255))
    d.text((355, 415), "AI", font=f(BOLD, 36), fill=(255,255,255))
    return save(img, i)

def client_email(i):
    img, d = base()
    d.text((145, 25), "SEND THE RESULT", font=f(BOLD, 42), fill=(255,255,255))

    d.rounded_rectangle([75, 105, 685, 470], radius=28, fill=(245,245,245))
    d.rectangle([75, 105, 685, 160], fill=(40,80,180))
    d.text((110, 123), "Message to business owner", font=f(BOLD, 24), fill=(255,255,255))

    d.text((115, 215), "I redesigned your website.", font=f(REG, 28), fill=(30,30,30))
    d.text((115, 260), "Here is the before and after.", font=f(REG, 28), fill=(30,30,30))
    d.rounded_rectangle([115, 330, 330, 395], radius=18, fill=(210,60,60))
    d.rounded_rectangle([410, 330, 625, 395], radius=18, fill=(60,190,120))
    d.text((160, 350), "BEFORE", font=f(BOLD, 24), fill=(255,255,255))
    d.text((470, 350), "AFTER", font=f(BOLD, 24), fill=(255,255,255))
    return save(img, i)

def payment(i):
    img, d = base()
    d.text((270, 25), "GET PAID", font=f(BOLD, 50), fill=(255,255,255))
    d.rounded_rectangle([180, 115, 580, 455], radius=35, fill=(20,120,70))
    d.rounded_rectangle([235, 165, 525, 405], radius=22, fill=(245,245,245))
    d.text((270, 205), "INVOICE PAID", font=f(BOLD, 30), fill=(30,30,30))
    d.text((310, 270), "$300", font=f(BOLD, 70), fill=(20,120,70))
    d.text((275, 365), "Website redesign", font=f(REG, 24), fill=(60,60,60))
    return save(img, i)

def content_calendar(i):
    img, d = base()
    d.text((160, 25), "CONTENT SYSTEM", font=f(BOLD, 42), fill=(255,255,255))
    d.rounded_rectangle([60, 105, 700, 460], radius=28, fill=(245,245,245))

    days = ["MON", "TUE", "WED", "THU", "FRI"]
    x = 95
    for day in days:
        d.rounded_rectangle([x, 155, x+100, 390], radius=16, fill=(30,35,55))
        d.text((x+18, 178), day, font=f(BOLD, 20), fill=(255,255,255))
        for y in [230, 280, 330]:
            d.rectangle([x+18, y, x+82, y+18], fill=(90,150,255))
        x += 120
    return save(img, i)

def problem_list(i):
    img, d = base()
    d.text((120, 25), "BORING PROBLEMS PAY", font=f(BOLD, 38), fill=(255,255,255))
    d.rounded_rectangle([95, 110, 665, 455], radius=28, fill=(245,245,245))

    items = ["Bad website", "No social media", "Slow replies", "No landing page"]
    y = 160
    for item in items:
        d.text((150, y), "X", font=f(BOLD, 34), fill=(220,60,60))
        d.text((210, y+3), item, font=f(BOLD, 30), fill=(30,30,30))
        y += 70
    return save(img, i)

def business_laptop(i):
    img, d = base()
    d.text((120, 25), "SIMPLE BUSINESS IDEA", font=f(BOLD, 38), fill=(255,255,255))
    d.rounded_rectangle([110, 125, 650, 430], radius=30, fill=(30,35,50))
    d.rounded_rectangle([160, 170, 600, 365], radius=20, fill=(10,15,25))
    d.rectangle([205, 210, 555, 230], fill=(80,150,255))
    d.rectangle([205, 265, 510, 285], fill=(70,210,140))
    d.rectangle([205, 320, 545, 340], fill=(180,180,190))
    d.text((210, 455), "BUILD → SELL → REPEAT", font=f(BOLD, 28), fill=(255,255,255))
    return save(img, i)

def make_assets(script_lines):
    scenes = plan_scenes(script_lines)
    paths = []

    makers = {
        "website_before_after": website_before_after,
        "ai_dashboard": ai_dashboard,
        "client_email": client_email,
        "payment": payment,
        "content_calendar": content_calendar,
        "problem_list": problem_list,
        "business_laptop": business_laptop,
    }

    print("\n=== MOCKUP SCENE PLAN ===")
    for i, scene in enumerate(scenes, start=1):
        print(i, scene["type"])
        maker = makers.get(scene["type"], business_laptop)
        paths.append(maker(i))
    print("=========================\n")

    return paths
'''

video_agent = r'''
import os
import subprocess
from datetime import datetime

def audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    return float(subprocess.check_output(cmd).decode().strip())

def create_scene(character_path, image_path, voice_path, output_path):
    duration = audio_duration(voice_path) + 0.15

    filter_complex = (
        "[0:v]scale=1080:1920[base];"
        "[1:v]scale=760:560[media];"
        "[base][media]overlay=x=160:y=625[tmp1];"
        "[tmp1]"
        "drawbox=x=140:y=605:w=800:h=600:color=white@0.9:t=6,"
        "drawbox=x=120:y=70:w=840:h=95:color=black@0.75:t=fill,"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='BUSINESS IDEA EXPLAINED':"
        "fontcolor=white:fontsize=48:x=(w-text_w)/2:y=92,"
        "drawbox=x=240:y=1660:w=600:h=75:color=black@0.75:t=fill,"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='FOLLOW FOR MORE IDEAS':"
        "fontcolor=white:fontsize=36:x=(w-text_w)/2:y=1678"
        "[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", character_path,
        "-loop", "1", "-i", image_path,
        "-i", voice_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "2:a",
        "-t", str(duration),
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    subprocess.run(cmd, check=True)

def make_video(script_lines, voice_paths, character_path, scene_paths):
    os.makedirs("ready_to_post", exist_ok=True)
    os.makedirs("content_factory/temp", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clips = []

    count = min(len(scene_paths), len(voice_paths))

    for i in range(count):
        clip_path = f"content_factory/temp/layout_scene_{timestamp}_{i}.mp4"
        print(f"Creating layout scene {i + 1}")

        create_scene(
            character_path,
            scene_paths[i],
            voice_paths[i],
            clip_path
        )

        clips.append(clip_path)

    list_path = f"content_factory/temp/layout_list_{timestamp}.txt"

    with open(list_path, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    output = f"ready_to_post/layout_style_{timestamp}.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output
    ], check=True)

    return output
'''

api_routes = r'''
from flask import jsonify
from agents.autonomous_manager import load_tasks

def register_agent_routes(app):
    @app.route("/agent-tasks")
    def agent_tasks():
        return jsonify(load_tasks())
'''

with open("agents/__init__.py", "w", encoding="utf-8") as f:
    f.write("")

files = {
    "agents/autonomous_manager.py": autonomous_manager,
    "agents/trend_agent.py": trend_agent,
    "agents/script_agent.py": script_agent,
    "agents/voice_agent.py": voice_agent,
    "agents/character_agent.py": character_agent,
    "agents/scene_planner_agent.py": scene_planner,
    "agents/visual_asset_agent.py": visual_asset_agent,
    "agents/video_agent.py": video_agent,
    "agents/agent_routes.py": api_routes,
}

for path, code in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(code.strip())

runner = r'''
from agents.autonomous_manager import start_yt_shorts_factory, open_videos_folder

videos = start_yt_shorts_factory(amount=5, upload=False)
open_videos_folder()

print("Created videos:")
for v in videos:
    print(v)
'''

with open("run_agent_mode.py", "w", encoding="utf-8") as f:
    f.write(runner.strip())

print("Klart! Agent mode installerad.")
print("")
print("Testa först med:")
print("python run_agent_mode.py")
print("")
print("För main.py:")
print("1. Lägg import:")
print("from agents.autonomous_manager import start_yt_shorts_factory, open_videos_folder")
print("")
print("2. Lägg i command-handlern:")
print('elif "starta agenter" in command or "start agents" in command:')
print('    speak("Jag startar agenterna.")')
print('    start_yt_shorts_factory(amount=5, upload=False)')
print('    speak("Fem videos är skapade.")')
print("")
print('elif "öppna videos" in command or "open videos" in command:')
print('    speak("Jag öppnar videos.")')
print('    open_videos_folder()')
print("")
print("Din gamla Jarvis HTML och vakna-läge ändras inte.")