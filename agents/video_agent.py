import os
import subprocess
from datetime import datetime

def audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    return float(subprocess.check_output(cmd).decode().strip())

def create_scene(character_path, image_path, voice_path, output_path):
    duration = audio_duration(voice_path) + 0.15

    filter_complex = (
        "[0:v]scale=1080:1920[base];"
        "[1:v]scale=760:560[media];"
        "[base][media]overlay=x=160:y=625[tmp1];"
        "[tmp1]"
        "drawbox=x=140:y=605:w=800:h=600:color=white@0.9:t=6,"
        "drawbox=x=120:y=70:w=840:h=95:color=black@0.75:t=fill,"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='BUSINESS IDEA EXPLAINED':"
        "fontcolor=white:fontsize=48:x=(w-text_w)/2:y=92,"
        "drawbox=x=240:y=1660:w=600:h=75:color=black@0.75:t=fill,"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='FOLLOW FOR MORE IDEAS':"
        "fontcolor=white:fontsize=36:x=(w-text_w)/2:y=1678"
        "[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", character_path,
        "-loop", "1", "-i", image_path,
        "-i", voice_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "2:a",
        "-t", str(duration),
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    subprocess.run(cmd, check=True)

def make_video(script_lines, voice_paths, character_path, scene_paths):
    os.makedirs("ready_to_post", exist_ok=True)
    os.makedirs("content_factory/temp", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clips = []

    count = min(len(scene_paths), len(voice_paths))

    for i in range(count):
        clip_path = f"content_factory/temp/layout_scene_{timestamp}_{i}.mp4"
        print(f"Creating layout scene {i + 1}")

        create_scene(
            character_path,
            scene_paths[i],
            voice_paths[i],
            clip_path
        )

        clips.append(clip_path)

    list_path = f"content_factory/temp/layout_list_{timestamp}.txt"

    with open(list_path, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    output = f"ready_to_post/layout_style_{timestamp}.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output
    ], check=True)

    return output