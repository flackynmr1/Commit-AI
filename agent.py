import webbrowser
import subprocess
import datetime
import json
from spotify import play_song, search_and_play
from memory import load_memory, save_memory

# -----------------------------
# MEMORY
# -----------------------------
memory = load_memory()

def remember(key, value):
    memory[key] = value
    save_memory(memory)


# -----------------------------
# INTENT ENGINE (SMART ROUTING)
# -----------------------------
def detect_intent(text: str):
    text = text.lower().strip()

    # --- MUSIC / SPOTIFY ---
    if any(x in text for x in ["spotify", "music", "play", "song", "playlist"]):
        return "music"

    # --- YOUTUBE / VIDEO ---
    if "youtube" in text or "video" in text:
        return "youtube"

    # --- WEATHER ---
    if "weather" in text or "väder" in text:
        return "weather"

    # --- TIME ---
    if "time" in text or "klocka" in text:
        return "time"

    # --- OPEN APPS ---
    if any(x in text for x in ["open", "start", "launch"]):
        return "open_app"

    return "unknown"


# -----------------------------
# DESKTOP CONTROL LAYER
# -----------------------------
def open_app(text):
    if "chrome" in text or "browser" in text:
        subprocess.Popen("start chrome", shell=True)

    elif "spotify" in text:
        subprocess.Popen("start spotify", shell=True)

    elif "youtube" in text:
        webbrowser.open("https://youtube.com")

    else:
        return "I don't know that app"
    return "Opening app"


# -----------------------------
# MAIN BRAIN
# -----------------------------
def run_agent(text):
    intent = detect_intent(text)

    # ---- MUSIC CONTROL ----
    if intent == "music":
        remember("last_command", text)

        # direct song play
        if "play" in text:
            song = text.replace("play", "").replace("spotify", "").strip()

            if song:
                search_and_play(song)
                return f"Spelar {song}"

            play_song("top hits")
            return "Spelar top hits"

    # ---- YOUTUBE ----
    if intent == "youtube":
        query = text.replace("youtube", "").strip()
        if not query:
            webbrowser.open("https://youtube.com")
        else:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return "Opening YouTube"

    # ---- WEATHER ----
    if intent == "weather":
        webbrowser.open("https://www.yr.no/nb/værvarsel/daglig-tabell/2-2692969/Sweden/Skåne/Malmö")
        return "Showing Malmö weather"

    # ---- TIME ----
    if intent == "time":
        now = datetime.datetime.now().strftime("%H:%M")
        return f"The time is {now}"

    # ---- APPS ----
    if intent == "open_app":
        return open_app(text)

    # ---- UNKNOWN (AI FALLBACK) ----
    return "I do not understand yet"