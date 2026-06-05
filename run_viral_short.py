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