from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "videos"
AUDIO_DIR = BASE_DIR / "audio"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "outputs"

for folder in [VIDEOS_DIR, AUDIO_DIR, ASSETS_DIR, OUTPUT_DIR]:
    folder.mkdir(exist_ok=True)

# Gratis Microsoft Edge TTS-röst
VOICE = "sv-SE-MattiasNeural"
# Alternativ:
# VOICE = "sv-SE-SofieNeural"

DEFAULT_AVATAR_IMAGE = ASSETS_DIR / "avatar.png"

# SadTalker om du installerar det senare
SADTALKER_DIR = BASE_DIR / "SadTalker"
USE_SADTALKER_IF_AVAILABLE = True
