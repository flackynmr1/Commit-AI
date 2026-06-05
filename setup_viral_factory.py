import os

os.makedirs("agents", exist_ok=True)
os.makedirs("content_factory/scripts", exist_ok=True)
os.makedirs("content_factory/voice", exist_ok=True)
os.makedirs("ready_to_post", exist_ok=True)

trend_agent = r'''
import random
import yt_dlp

SEEDS = [
    "AI tools shorts",
    "make money online shorts",
    "productivity shorts",
    "business motivation shorts",
    "side hustle shorts",
    "tech facts shorts"
]

FALLBACK_TRENDS = [
    "3 AI tools people are sleeping on",
    "The biggest mistake beginners make online",
    "How to build systems that make money while you sleep",
    "This habit separates winners from average people",
    "AI is changing side hustles forever"
]

def get_viral_idea():
    query = random.choice(SEEDS)

    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "default_search": "ytsearch10"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(query, download=False)

        titles = []
        for item in data.get("entries", []):
            title = item.get("title")
            if title:
                titles.append(title)

        if titles:
            base = random.choice(titles)
            return {
                "source_title": base,
                "idea": "Gör en egen svensk short inspirerad av formatet: " + base
            }

    except Exception as e:
        print("Trend-agent fallback:", e)

    idea = random.choice(FALLBACK_TRENDS)
    return {
        "source_title": idea,
        "idea": idea
    }
'''

script_agent = r'''
import random

def make_script(trend):
    source = trend["source_title"]

    hooks = [
        "Det här fattar nästan ingen.",
        "Det här kan förändra hur du ser på AI.",
        "Om du vill tjäna pengar online, lyssna nu.",
        "Här är en grej jag önskar jag visste tidigare.",
        "De flesta gör detta helt fel."
    ]

    hook = random.choice(hooks)

    title = "Det här kan ändra allt #Shorts"

    script_lines = [
        hook,
        "Jag såg ett viralt format om: " + source,
        "Men här är min egna version.",
        "Steg ett: hitta ett problem folk redan bryr sig om.",
        "Steg två: gör en enkel lösning med AI.",
        "Steg tre: posta varje dag och låt datan bestämma vad som funkar.",
        "Det är så du bygger ett system, inte bara en video.",
        "Följ för fler AI och automation tips."
    ]

    description = (
        "Skapad automatiskt av Jarvis AI.\n"
        "Original idé, inspirerad av virala format men inte kopierad.\n\n"
        "#Shorts #AI #Automation #Business #Sverige"
    )

    return title, script_lines, description
'''

voice_agent = r'''
import os
import subprocess
from datetime import datetime

def make_voice(script_lines):
    os.makedirs("content_factory/voice", exist_ok=True)

    text = " ".join(script_lines)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    voice_path = f"content_factory/voice/voice_{timestamp}.mp3"

    cmd = [
        "python",
        "-m",
        "edge_tts",
        "--voice",
        "sv-SE-MattiasNeural",
        "--text",
        text,
        "--write-media",
        voice_path
    ]

    subprocess.run(cmd, check=True)
    return voice_path
'''

video_agent = r'''
import os
import subprocess
import random
from datetime import datetime

FONT = "C\\:/Windows/Fonts/arial.ttf"

def clean(text):
    bad = ["'", '"', ":", "\\", "|", "{", "}", "[", "]"]
    for b in bad:
        text = text.replace(b, "")
    return text

def get_audio_duration(audio_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    result = subprocess.check_output(cmd).decode().strip()
    return float(result)

def make_video(script_lines, voice_path):
    os.makedirs("ready_to_post", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = f"ready_to_post/viral_short_{timestamp}.mp4"

    duration = max(18, get_audio_duration(voice_path) + 1)

    filters = []

    total_lines = len(script_lines)
    segment = duration / total_lines

    for i, line in enumerate(script_lines):
        start = i * segment
        end = (i + 1) * segment
        text = clean(line)

        filters.append(
            f"drawtext=fontfile='{FONT}':"
            f"text='{text}':"
            "fontcolor=white:"
            "fontsize=62:"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2:"
            "box=1:"
            "boxcolor=black@0.65:"
            "boxborderw=35:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )

    vf = ",".join(filters)

    backgrounds = [
        f"testsrc2=s=1080x1920:d={duration}:rate=30",
        f"mandelbrot=s=1080x1920:rate=30",
        f"color=c=0x111111:s=1080x1920:d={duration}:rate=30"
    ]

    bg = random.choice(backgrounds)

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", bg,
        "-i", voice_path,
        "-vf", vf,
        "-shortest",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-c:a", "aac",
        video_path
    ]

    subprocess.run(cmd, check=True)
    return video_path
'''

main_runner = r'''
from agents.trend_agent import get_viral_idea
from agents.script_agent import make_script
from agents.voice_agent import make_voice
from agents.video_agent import make_video
from agents.youtube_upload_agent import upload_short

trend = get_viral_idea()
print("Viral idé:", trend)

title, script_lines, description = make_script(trend)

print("Skapar röst...")
voice_path = make_voice(script_lines)

print("Skapar video...")
video_path = make_video(script_lines, voice_path)

print("Laddar upp till YouTube...")
upload_short(
    video_path=video_path,
    title=title,
    description=description,
    privacy="public"
)

print("Klar! Jarvis skapade och publicerade en viral-style AI Short.")
'''

with open("agents/trend_agent.py", "w", encoding="utf-8") as f:
    f.write(trend_agent.strip())

with open("agents/script_agent.py", "w", encoding="utf-8") as f:
    f.write(script_agent.strip())

with open("agents/voice_agent.py", "w", encoding="utf-8") as f:
    f.write(voice_agent.strip())

with open("agents/video_agent.py", "w", encoding="utf-8") as f:
    f.write(video_agent.strip())

with open("run_viral_short.py", "w", encoding="utf-8") as f:
    f.write(main_runner.strip())

print("Klart. Kör nu:")
print("python run_viral_short.py")