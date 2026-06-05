from pathlib import Path
import subprocess
import sys

from config import SADTALKER_DIR, DEFAULT_AVATAR_IMAGE, VIDEOS_DIR


def sadtalker_available() -> bool:
    inference_file = SADTALKER_DIR / "inference.py"
    return SADTALKER_DIR.exists() and inference_file.exists() and DEFAULT_AVATAR_IMAGE.exists()


def create_avatar_video(audio_path: Path, output_name: str = "avatar_business_video.mp4") -> Path | None:
    """
    Kräver att du själv installerar SadTalker i mappen SadTalker.
    Detta är frivilligt. Om det inte finns kör systemet vanlig slide-video istället.
    """

    if not sadtalker_available():
        return None

    VIDEOS_DIR.mkdir(exist_ok=True)

    cmd = [
        sys.executable,
        "inference.py",
        "--driven_audio", str(audio_path),
        "--source_image", str(DEFAULT_AVATAR_IMAGE),
        "--result_dir", str(VIDEOS_DIR),
        "--still",
        "--preprocess", "full",
    ]

    print("Startar SadTalker...")
    subprocess.run(cmd, cwd=str(SADTALKER_DIR), check=True)

    print("SadTalker klar. Kolla videos-mappen.")
    return VIDEOS_DIR / output_name
