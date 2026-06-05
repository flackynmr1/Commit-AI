from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from config import VIDEOS_DIR, OUTPUT_DIR


def _get_font(size=48):
    possible_fonts = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for font in possible_fonts:
        if Path(font).exists():
            return ImageFont.truetype(font, size)

    return ImageFont.load_default()


def split_text(text: str, max_words: int = 22):
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i + max_words]))

    return chunks


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def make_slide_image(text: str, index: int, total: int, output_path: Path):
    width, height = 1280, 720
    img = Image.new("RGB", (width, height), (12, 12, 18))
    draw = ImageDraw.Draw(img)

    title_font = _get_font(54)
    body_font = _get_font(44)
    small_font = _get_font(26)

    title = "AI Business Explainer"
    draw.text((70, 55), title, fill=(255, 255, 255), font=title_font)

    lines = wrap_text(draw, text, body_font, width - 140)

    y = 210
    for line in lines[:7]:
        draw.text((70, y), line, fill=(235, 235, 235), font=body_font)
        y += 60

    progress = f"{index}/{total}"
    draw.text((70, height - 70), progress, fill=(160, 160, 160), font=small_font)

    img.save(output_path)


def create_simple_video(script: str, audio_path: Path, output_name: str = "business_video.mp4") -> Path:
    VIDEOS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    audio = AudioFileClip(str(audio_path))
    chunks = split_text(script, max_words=20)

    total_duration = audio.duration
    duration_per_slide = max(2.5, total_duration / max(len(chunks), 1))

    clips = []

    for i, chunk in enumerate(chunks, start=1):
        slide_path = OUTPUT_DIR / f"slide_{i}.png"
        make_slide_image(chunk, i, len(chunks), slide_path)

        clip = ImageClip(str(slide_path)).set_duration(duration_per_slide)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    output_path = VIDEOS_DIR / output_name
    video.write_videofile(
        str(output_path),
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    audio.close()
    video.close()

    return output_path
