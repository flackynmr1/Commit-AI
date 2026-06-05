import os

os.makedirs("agents", exist_ok=True)
os.makedirs("dashboard", exist_ok=True)
os.makedirs("ready_to_post", exist_ok=True)
os.makedirs("content_factory/logs", exist_ok=True)

autonomous_manager = r'''
import os
import json
import time
import webbrowser
from datetime import datetime

from agents.trend_agent import get_viral_idea
from agents.script_agent import make_script
from agents.voice_agent import make_voice
from agents.visual_asset_agent import make_assets
from agents.character_agent import create_character_image
from agents.video_agent import make_video

TASK_FILE = "content_factory/logs/tasks.json"

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

def save_tasks(tasks):
    os.makedirs("content_factory/logs", exist_ok=True)
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def log(tasks, agent, status, detail):
    item = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "status": status,
        "detail": detail
    }
    tasks.append(item)
    save_tasks(tasks)
    print(f"[{item['time']}] {agent}: {status} - {detail}")

def open_videos_folder():
    path = os.path.abspath("ready_to_post")
    os.startfile(path)

def start_yt_shorts_factory(amount=5, upload=False):
    tasks = []
    save_tasks(tasks)

    print("\n==============================")
    print(" JARVIS YT SHORTS MISSION MODE")
    print("==============================\n")

    log(tasks, "Jarvis", "STARTING", "Booting autonomous YouTube Shorts agents")

    for agent in AGENTS:
        log(tasks, agent, "ONLINE", "Agent initialized")
        time.sleep(0.25)

    created_videos = []

    for n in range(1, amount + 1):
        log(tasks, "Jarvis", "MISSION", f"Creating video {n}/{amount}")

        trend = get_viral_idea()
        log(tasks, "Trend Agent", "DONE", trend.get("source_title", "Trend selected"))

        title, script_lines, description = make_script(trend)
        log(tasks, "Script Agent", "DONE", title)

        scene_paths = make_assets(script_lines)
        log(tasks, "Visual Agent", "DONE", f"{len(scene_paths)} visuals created")

        voice_paths = make_voice(script_lines)
        log(tasks, "Voice Agent", "DONE", f"{len(voice_paths)} voice scenes created")

        character_path = create_character_image()
        log(tasks, "Character Agent", "DONE", "Character layout created")

        video_path = make_video(script_lines, voice_paths, character_path, scene_paths)
        created_videos.append(video_path)
        log(tasks, "Video Agent", "DONE", video_path)

        if upload:
            try:
                from agents.youtube_upload_agent import upload_short
                upload_short(video_path, title, description, privacy="public")
                log(tasks, "Upload Agent", "DONE", "Uploaded to YouTube Shorts")
            except Exception as e:
                log(tasks, "Upload Agent", "FAILED", str(e))
        else:
            log(tasks, "Upload Agent", "SKIPPED", "Upload disabled because YouTube limit/test mode")

    log(tasks, "Analytics Agent", "READY", "Views/revenue tracking can be connected next")
    log(tasks, "Learning Agent", "READY", "Will use future analytics to improve topics")
    log(tasks, "Jarvis", "FINISHED", f"Created {len(created_videos)} videos")

    print("\nVideos created:")
    for v in created_videos:
        print("-", v)

    return created_videos
'''

dashboard_html = r'''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Jarvis Agents</title>
  <style>
    body {
      margin: 0;
      background: radial-gradient(circle at top, #1d2b64, #050510 65%);
      color: white;
      font-family: Arial, sans-serif;
      overflow: hidden;
    }
    .boot {
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
    }
    h1 {
      font-size: 54px;
      letter-spacing: 4px;
      animation: glow 1.5s infinite alternate;
    }
    @keyframes glow {
      from { text-shadow: 0 0 10px #00eaff; }
      to { text-shadow: 0 0 35px #00eaff; }
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 18px;
      width: 85%;
      margin-top: 40px;
    }
    .agent {
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(0,234,255,0.4);
      border-radius: 18px;
      padding: 20px;
      text-align: center;
      box-shadow: 0 0 20px rgba(0,234,255,0.15);
    }
    .pulse {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: #00ff9d;
      margin: 10px auto;
      animation: pulse 1s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(1); opacity: .5; }
      100% { transform: scale(1.6); opacity: 1; }
    }
    #tasks {
      position: absolute;
      bottom: 30px;
      left: 50px;
      right: 50px;
      height: 220px;
      overflow: auto;
      background: rgba(0,0,0,0.35);
      border-radius: 18px;
      padding: 20px;
      font-size: 18px;
    }
  </style>
</head>
<body>
  <div class="boot">
    <h1>JARVIS AGENT MODE</h1>
    <p>YT Shorts Factory Online</p>

    <div class="grid">
      <div class="agent">Trend Agent<div class="pulse"></div></div>
      <div class="agent">Script Agent<div class="pulse"></div></div>
      <div class="agent">Visual Agent<div class="pulse"></div></div>
      <div class="agent">Voice Agent<div class="pulse"></div></div>
      <div class="agent">Character Agent<div class="pulse"></div></div>
      <div class="agent">Video Agent<div class="pulse"></div></div>
      <div class="agent">Analytics Agent<div class="pulse"></div></div>
      <div class="agent">Learning Agent<div class="pulse"></div></div>
    </div>

    <div id="tasks">Loading tasks...</div>
  </div>

<script>
async function loadTasks() {
  try {
    const res = await fetch("../content_factory/logs/tasks.json?x=" + Date.now());
    const data = await res.json();
    document.getElementById("tasks").innerHTML = data.slice(-8).map(t =>
      `<div>[${t.time}] <b>${t.agent}</b> — ${t.status}: ${t.detail}</div>`
    ).join("");
  } catch(e) {
    document.getElementById("tasks").innerHTML = "Waiting for agents...";
  }
}
setInterval(loadTasks, 1000);
loadTasks();
</script>
</body>
</html>
'''

runner = r'''
from agents.autonomous_manager import start_yt_shorts_factory, open_videos_folder

# Skapar 5 videos när du kör filen.
# Upload är avstängd tills YouTube-limit är tillbaka.
start_yt_shorts_factory(amount=5, upload=False)

open_videos_folder()
'''

with open("agents/autonomous_manager.py", "w", encoding="utf-8") as f:
    f.write(autonomous_manager.strip())

with open("dashboard/jarvis_agents.html", "w", encoding="utf-8") as f:
    f.write(dashboard_html.strip())

with open("run_autonomous_jarvis.py", "w", encoding="utf-8") as f:
    f.write(runner.strip())

print("Klart.")
print("Skapade:")
print("- agents/autonomous_manager.py")
print("- dashboard/jarvis_agents.html")
print("- run_autonomous_jarvis.py")
print("")
print("Kör:")
print("python run_autonomous_jarvis.py")