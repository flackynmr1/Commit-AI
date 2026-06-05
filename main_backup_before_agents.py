# =========================
# MAIN.PY
# =========================

from flask import Flask, render_template_string, request, jsonify

import threading
import webbrowser
import subprocess
import os
import ctypes
import time
import asyncio
import uuid

import edge_tts

import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr

from playsound import playsound

from askai import ask_ai, remember
from calendar_tools import get_events_for_day, add_calendar_event

import spotipy
from spotipy.oauth2 import SpotifyOAuth


# =========================
# SPOTIFY
# =========================

SPOTIFY_CLIENT_ID = "2da5bbf0aadb4c8d9224cb29eeb3c0dd"
SPOTIFY_CLIENT_SECRET = "38387f1e98c142c884c3e6f3bcb5788f"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPE = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing"
)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )
)

# =========================
# APP
# =========================

app = Flask(__name__)

URL = "http://127.0.0.1:5000"

MIC_DEVICE = None
MIC_SAMPLE_RATE = 16000

is_speaking = False
jarvis_awake = False
browser_process = None

speech_lock = threading.Lock()

WAKE_WORDS = [
    "jarvis",
    "vakna",
    "wake up",
    "yo jarvis"
]

SLEEP_WORDS = [
    "sov",
    "somna",
    "sleep",
    "godnatt",
    "lägg dig",
    "stäng ner",
    "shutdown"
]


# =========================
# SPEAK
# =========================

def speak(text):

    global is_speaking

    async def make_voice(file_path):

        communicate = edge_tts.Communicate(
            text,
            voice="sv-SE-MattiasNeural",
            rate="+5%"
        )

        await communicate.save(file_path)

    def run():

        global is_speaking

        file_path = f"jarvis_voice_{uuid.uuid4().hex}.mp3"

        with speech_lock:

            is_speaking = True

            try:

                asyncio.run(
                    make_voice(file_path)
                )

                play_thread = threading.Thread(
                    target=playsound,
                    args=(file_path,),
                    daemon=True
                )

                play_thread.start()

                while play_thread.is_alive():

                    heard = listen_once(
                        seconds=1,
                        allow_interrupt=True
                    )

                    if heard:

                        print("AVBRYTER:", heard)

                        is_speaking = False

                        answer = command(heard)

                        if not answer:
                            answer = ask_ai(heard)

                        print("SVAR:", answer)

                        speak(answer)

                        break

                    time.sleep(0.1)

                try:
                    os.remove(file_path)
                except:
                    pass

            except Exception as e:

                print("TTS FEL:", e)

            is_speaking = False

    threading.Thread(
        target=run,
        daemon=True
    ).start()


# =========================
# MICROPHONE
# =========================

def setup_microphone():

    global MIC_DEVICE
    global MIC_SAMPLE_RATE

    devices = sd.query_devices()

    print("Söker efter fungerande mikrofon...")

    for i, device in enumerate(devices):

        name = str(device["name"]).lower()

        if (
            device["max_input_channels"] > 0
            and (
                "yeti" in name
                or "microphone" in name
                or "mic" in name
            )
        ):

            try:

                rate = int(device["default_samplerate"])

                sd.rec(
                    int(0.2 * rate),
                    samplerate=rate,
                    channels=1,
                    dtype="int16",
                    device=i
                )

                sd.wait()

                MIC_DEVICE = i
                MIC_SAMPLE_RATE = rate

                print(
                    "MIC:",
                    MIC_DEVICE,
                    device["name"],
                    MIC_SAMPLE_RATE
                )

                return

            except Exception as e:
                print("Mic funkade inte:", e)

    print("Ingen fungerande mic hittades.")


# =========================
# LISTEN
# =========================

def listen_once(seconds=3, allow_interrupt=False):

    global is_speaking

    if is_speaking and not allow_interrupt:
        return ""

    if MIC_DEVICE is None:
        return ""

    filename = "voice.wav"

    try:

        audio = sd.rec(
            int(seconds * MIC_SAMPLE_RATE),
            samplerate=MIC_SAMPLE_RATE,
            channels=1,
            dtype="int16",
            device=MIC_DEVICE
        )

        sd.wait()

    except Exception as e:

        print("MIC FEL:", e)

        return ""

    write(filename, MIC_SAMPLE_RATE, audio)

    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:

        data = recognizer.record(source)

    try:

        return recognizer.recognize_google(
            data,
            language="sv-SE"
        ).lower()

    except:

        try:

            return recognizer.recognize_google(
                data,
                language="en-US"
            ).lower()

        except:

            return ""


# =========================
# WINDOW
# =========================

def find_browser():

    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]

    for p in paths:

        if os.path.exists(p):
            return p

    return None


def press_key(hex_code):

    ctypes.windll.user32.keybd_event(
        hex_code,
        0,
        0,
        0
    )

    ctypes.windll.user32.keybd_event(
        hex_code,
        0,
        2,
        0
    )


def open_jarvis_window():

    global browser_process

    browser = find_browser()

    if browser:

        profile_dir = os.path.abspath(
            "jarvis_browser_profile"
        )

        browser_process = subprocess.Popen([
            browser,
            f"--app={URL}",
            f"--user-data-dir={profile_dir}",
            "--new-window",
            "--start-fullscreen"
        ])

        time.sleep(1.5)

        press_key(0x7A)

    else:

        webbrowser.open(URL)


def close_jarvis_window():

    global browser_process

    try:

        if browser_process:

            subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(browser_process.pid),
                    "/T",
                    "/F"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            browser_process = None

    except:
        pass


def show_desktop():

    try:

        ctypes.windll.user32.keybd_event(0x5B,0,0,0)
        ctypes.windll.user32.keybd_event(0x44,0,0,0)
        ctypes.windll.user32.keybd_event(0x44,0,2,0)
        ctypes.windll.user32.keybd_event(0x5B,0,2,0)

    except:
        pass


# =========================
# SPOTIFY
# =========================

def spotify_play(query):

    try:

        devices = sp.devices()

        if not devices["devices"]:
            return "Öppna Spotify först bror."

        results = sp.search(
            q=query,
            type="track",
            limit=1
        )

        tracks = results["tracks"]["items"]

        if not tracks:
            return "Hittade inte låten bror."

        track = tracks[0]

        sp.start_playback(
            device_id=devices["devices"][0]["id"],
            uris=[track["uri"]]
        )

        return f"Spelar {track['name']}."

    except:
        return "Spotify strular bror."


# =========================
# FAST CHAT
# =========================

def fast_chat(t):

    if "hur mår du" in t:
        return "Jag mår bra bror."

    if "hur är läget" in t:
        return "Det är chill bror."

    if "vad gör du" in t:
        return "Lyssnar på dig cuz."

    if "hej" in t or "hallå" in t:
        return "Tja bror."

    return None


# =========================
# COMMANDS
# =========================

def command(text):

    global jarvis_awake

    t = text.lower().strip()

    # CALENDAR

    if "vad har jag idag" in t:
        return get_events_for_day(0)

    if "vad händer idag" in t:
        return get_events_for_day(0)

    if "vad händer imorgon" in t:
        return get_events_for_day(1)

    if "vad har jag imorgon" in t:
        return get_events_for_day(1)

    if "vad ska jag göra imorgon" in t:
        return get_events_for_day(1)

    if (
        "lägg till" in t
        and (
            "kalender" in t
            or "möte" in t
            or "event" in t
        )
    ):
        return add_calendar_event(text)

    quick = fast_chat(t)

    if quick:
        return quick

    # SLEEP

    if any(word in t for word in SLEEP_WORDS):

        jarvis_awake = False

        speak("Okej bror.")

        time.sleep(1)

        close_jarvis_window()

        show_desktop()

        return "Jarvis sover."

    # MEMORY

    if t.startswith("kom ihåg"):

        memory_text = text.replace(
            "kom ihåg",
            "",
            1
        ).strip()

        return remember(memory_text)

    # MUSIC

    if t.startswith("spela "):

        query = text.replace(
            "spela",
            "",
            1
        ).strip()

        return spotify_play(query)

    if "nästa låt" in t:

        try:
            sp.next_track()
            return "Nästa låt bror."
        except:
            return "Spotify strular."

    if "förra låten" in t:

        try:
            sp.previous_track()
            return "Förra låten."
        except:
            return "Spotify strular."

    if "pausa" in t:

        try:
            sp.pause_playback()
            return "Pausar."
        except:
            return "Spotify strular."

    if "fortsätt" in t:

        try:
            sp.start_playback()
            return "Fortsätter."
        except:
            return "Spotify strular."

    return None


# =========================
# WAKE LISTENER
# =========================

def wake_listener():

    global jarvis_awake

    while True:

        text = listen_once(seconds=3)

        if not text:
            continue

        print("HÖRDE:", text)

        if not jarvis_awake:

            if any(word in text for word in WAKE_WORDS):

                jarvis_awake = True

                open_jarvis_window()

                speak("Yes bror?")

        else:

            answer = command(text)

            if not answer:
                answer = ask_ai(text)

            print("SVAR:", answer)

            speak(answer)


# =========================
# HTML
# =========================

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>JARVIS</title>

<style>

body{
margin:0;
background:#030608;
overflow:hidden;
font-family:Consolas;
color:#00f7ff;
}

.center{
height:100vh;
display:flex;
justify-content:center;
align-items:center;
flex-direction:column;
}

.title{
font-size:60px;
letter-spacing:10px;
text-shadow:0 0 25px #00f7ff;
}

.orb{
width:220px;
height:220px;
border-radius:50%;

background:
radial-gradient(circle,
white 0%,
#00f7ff 12%,
#003840 45%,
transparent 70%);

box-shadow:
0 0 35px #00f7ff,
0 0 100px #00f7ff,
inset 0 0 30px white;

animation:pulse 1.6s infinite alternate;
margin:30px;
}

@keyframes pulse{
from{transform:scale(.95)}
to{transform:scale(1.08)}
}

</style>
</head>

<body>

<div class="center">

<div class="title">
JARVIS
</div>

<div class="orb"></div>

</div>

</body>
</html>
"""


# =========================
# ROUTES
# =========================

@app.route("/")
def home():

    return render_template_string(
        HTML
    )


@app.route("/ask", methods=["POST"])
def ask():

    text = request.get_json().get(
        "text",
        ""
    )

    answer = command(text)

    if not answer:
        answer = ask_ai(text)

    speak(answer)

    return jsonify({
        "answer": answer
    })


# =========================
# START
# =========================

if __name__ == "__main__":

    print("STARTAR JARVIS...")

    setup_microphone()

    threading.Thread(
        target=wake_listener,
        daemon=True
    ).start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )