from agents.trend_agent import get_viral_idea
from agents.script_agent import make_script
from agents.voice_agent import make_voice
from agents.visual_asset_agent import make_assets
from agents.character_agent import create_character_image
from agents.video_agent import make_video

print("Finding trend...")
trend = get_viral_idea()

print("Trend inspiration:", trend["source_title"])

title, script_lines, description = make_script(trend)

print("\n=== SCRIPT ===")
for line in script_lines:
    print("-", line)

print("\nCreating visuals...")
scene_paths = make_assets(script_lines)

print("Creating voice...")
voice_paths = make_voice(script_lines)

print("Creating character...")
character_path = create_character_image()

print("Building final video...")
video_path = make_video(
    script_lines,
    voice_paths,
    character_path,
    scene_paths
)

print("\n================================")
print("VIDEO CREATED SUCCESSFULLY")
print("Saved to:")
print(video_path)
print("================================")
print("\nUpload disabled for testing.")
print("Watch the video first and improve it.")