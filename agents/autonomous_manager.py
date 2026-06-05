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