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


def clean_text(text):
    bad_chars = ["'", '"', ":", "\\", "/", "|"]
    for char in bad_chars:
        text = text.replace(char, "")
    return text.replace("\n", " ").strip()


def create_ai_short():
    os.makedirs("content_factory/scripts", exist_ok=True)
    os.makedirs("ready_to_post", exist_ok=True)

    idea = random.choice(IDEAS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    title = idea[:80] + " #Shorts"
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
    text = clean_text(script)

    font_path = "C\\:/Windows/Fonts/arial.ttf"

    drawtext_filter = (
        f"drawtext=fontfile='{font_path}':"
        f"text='{text}':"
        "fontcolor=white:"
        "fontsize=54:"
        "x=(w-text_w)/2:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.6:"
        "boxborderw=30"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920:d=18",
        "-vf", drawtext_filter,
        "-r", "30",
        "-pix_fmt", "yuv420p",
        video_path
    ]

    print("Skapar AI-video...")
    subprocess.run(cmd, check=True)

    print("Video skapad:", video_path)
    return video_path, title, description