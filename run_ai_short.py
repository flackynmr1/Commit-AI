from agents.content_factory_agent import create_ai_short
from agents.youtube_upload_agent import upload_short

video_path, title, description = create_ai_short()

upload_short(
    video_path=video_path,
    title=title,
    description=description,
    privacy="private"
)

print("Klar! Video skapad och uppladdad.")