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