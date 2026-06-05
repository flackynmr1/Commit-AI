from agents.autonomous_manager import start_yt_shorts_factory, open_videos_folder

videos = start_yt_shorts_factory(amount=5, upload=False)
open_videos_folder()

print("Created videos:")
for v in videos:
    print(v)