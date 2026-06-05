from agents.autonomous_manager import start_yt_shorts_factory, open_videos_folder

# Skapar 5 videos när du kör filen.
# Upload är avstängd tills YouTube-limit är tillbaka.
start_yt_shorts_factory(amount=5, upload=False)

open_videos_folder()