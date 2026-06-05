from pathlib import Path
import time

from script_writer import make_business_script, make_short_script
from tts_edge import create_voice
from simple_video import create_simple_video
from sadtalker_runner import create_avatar_video, sadtalker_available
from config import USE_SADTALKER_IF_AVAILABLE


def create_ai_business_video(idea: str, use_avatar: bool = True) -> Path:
    print("Skriver manus...")
    script = make_business_script(idea)

    print("Skapar gratis svensk AI-röst...")
    audio_path = create_voice(script, filename=f"voice_{int(time.time())}.mp3")

    if use_avatar and USE_SADTALKER_IF_AVAILABLE and sadtalker_available():
        print("SadTalker hittad. Skapar avatar-video...")
        avatar_result = create_avatar_video(audio_path)
        if avatar_result:
            return avatar_result

    print("Skapar gratis slide-video...")
    output_path = create_simple_video(
        script=script,
        audio_path=audio_path,
        output_name=f"business_video_{int(time.time())}.mp4"
    )

    return output_path


if __name__ == "__main__":
    idea = input("Skriv din business-idé: ")
    video = create_ai_business_video(idea)
    print(f"\nKLART! Video skapad här:\n{video}")
