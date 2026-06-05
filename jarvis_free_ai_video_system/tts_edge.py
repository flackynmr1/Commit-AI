import asyncio
from pathlib import Path
import edge_tts
from config import AUDIO_DIR, VOICE


async def _save_tts(text: str, output_path: Path, voice: str):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(output_path))


def create_voice(text: str, filename: str = "voice.mp3", voice: str = VOICE) -> Path:
    AUDIO_DIR.mkdir(exist_ok=True)
    output_path = AUDIO_DIR / filename

    asyncio.run(_save_tts(text, output_path, voice))

    return output_path
