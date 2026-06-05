# =========================
# MAIN.PY
# =========================

from flask import Flask, render_template_string, request, jsonify
from agents.autonomous_manager import start_yt_shorts_factory, open_videos_folder

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

    # AGENTS

    if "starta agenter" in t or "start agents" in t:
        speak("Jag startar agenterna nu.")

        start_yt_shorts_factory(
            amount=5,
            upload=False
        )

        return "Fem videos är skapade."

    if "öppna videos" in t or "open videos" in t:
        open_videos_folder()
        return "Här är videos-mappen."

    # CALENDAR

    if "vad har jag idag" in t:
        return get_events_for_day(0)

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
<html lang="sv">
<head>
<meta charset="UTF-8">
<title>JARVIS</title>
<style>
*{box-sizing:border-box}
body{
  margin:0;
  background:#02050a;
  color:white;
  font-family:Arial,sans-serif;
  overflow:hidden;
}
#app{
  width:100vw;
  height:100vh;
  position:relative;
  background:
    radial-gradient(circle at center, rgba(0,255,255,.16), transparent 30%),
    linear-gradient(120deg,#02050a,#06111f,#02050a);
}
.grid{
  position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(0,255,255,.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,255,255,.06) 1px, transparent 1px);
  background-size:40px 40px;
}
.title{
  position:absolute;top:30px;width:100%;
  text-align:center;font-size:46px;letter-spacing:10px;
  text-shadow:0 0 28px #00eaff;
}
.status{
  position:absolute;top:92px;width:100%;
  text-align:center;color:#8ffaff;font-size:18px;
}
.face{
  position:absolute;left:50%;top:44%;
  transform:translate(-50%,-50%);
  width:370px;height:470px;border-radius:45%;
  background:radial-gradient(circle,rgba(0,234,255,.25),transparent 65%);
  filter:drop-shadow(0 0 35px #00eaff);
}
.face:before{
  content:"";position:absolute;inset:35px;border-radius:45%;
  border:1px solid rgba(0,255,255,.45);
  box-shadow:0 0 45px #00eaff inset;
}
.eye{
  position:absolute;top:188px;width:66px;height:20px;
  background:#eaffff;border-radius:50%;
  box-shadow:0 0 25px #00eaff;
}
.eye.left{left:92px}
.eye.right{right:92px}
.mouth{
  position:absolute;left:50%;bottom:112px;
  transform:translateX(-50%);
  width:135px;height:20px;
  border-bottom:3px solid #eaffff;
  box-shadow:0 0 16px #00eaff;
}
.agent{
  position:absolute;width:190px;padding:14px;
  border:1px solid rgba(0,234,255,.45);
  background:rgba(0,20,35,.65);
  border-radius:18px;text-align:center;
  opacity:.38;transition:.35s;
  box-shadow:0 0 12px rgba(0,234,255,.12);
}
.agent.active{
  opacity:1;transform:scale(1.06);
  box-shadow:0 0 35px #00eaff;
}
.agent small{color:#8ffaff}
.spark{
  position:absolute;width:20px;height:20px;border-radius:50%;
  background:#eaffff;box-shadow:0 0 25px #00eaff,0 0 60px #00eaff;
  display:none;z-index:20;
}
#tasks{
  position:absolute;left:40px;right:40px;bottom:35px;height:165px;
  background:rgba(0,0,0,.48);
  border:1px solid rgba(0,234,255,.35);
  border-radius:18px;padding:18px;overflow:auto;font-size:16px;
}
#chat{
  position:absolute;left:50%;bottom:220px;transform:translateX(-50%);
  width:620px;display:flex;gap:10px;
}
#text{
  flex:1;padding:14px;border-radius:14px;border:1px solid #00eaff;
  background:rgba(0,0,0,.45);color:white;font-size:16px;
}
button{
  padding:14px 22px;border-radius:14px;border:0;
  background:#00eaff;color:#001014;font-weight:bold;
}
</style>
</head>
<body>
<div id="app">
  <div class="grid"></div>
  <div class="title">JARVIS</div>
  <div class="status" id="status">Waiting for wake command...</div>

  <div class="face">
    <div class="eye left"></div>
    <div class="eye right"></div>
    <div class="mouth"></div>
  </div>

  <div id="spark" class="spark"></div>

  <div class="agent" id="a0" style="left:70px;top:160px;">Trend Agent<br><small>offline</small></div>
  <div class="agent" id="a1" style="right:70px;top:160px;">Script Agent<br><small>offline</small></div>
  <div class="agent" id="a2" style="left:120px;top:350px;">Visual Agent<br><small>offline</small></div>
  <div class="agent" id="a3" style="right:120px;top:350px;">Voice Agent<br><small>offline</small></div>
  <div class="agent" id="a4" style="left:70px;top:540px;">Character Agent<br><small>offline</small></div>
  <div class="agent" id="a5" style="right:70px;top:540px;">Video Agent<br><small>offline</small></div>
  <div class="agent" id="a6" style="left:350px;top:680px;">Analytics Agent<br><small>standby</small></div>
  <div class="agent" id="a7" style="right:350px;top:680px;">Learning Agent<br><small>standby</small></div>

  <div id="chat">
    <input id="text" placeholder="Skriv till Jarvis...">
    <button onclick="send()">Skicka</button>
  </div>

  <div id="tasks">Agent log waiting...</div>
</div>

<script>
const agents=[...document.querySelectorAll(".agent")];
const spark=document.getElementById("spark");
const statusBox=document.getElementById("status");
let lastCount=0;

function center(el){
  const r=el.getBoundingClientRect();
  return {x:r.left+r.width/2,y:r.top+r.height/2}
}
function activateAgent(i){
  if(!agents[i])return;
  spark.style.display="block";
  const face={x:window.innerWidth/2,y:window.innerHeight/2};
  const target=center(agents[i]);
  spark.animate([
    {left:face.x+"px",top:face.y+"px"},
    {left:target.x+"px",top:target.y+"px"}
  ],{duration:520,fill:"forwards",easing:"ease-out"});
  setTimeout(()=>{
    agents[i].classList.add("active");
    agents[i].querySelector("small").innerText="online";
  },430);
}
function agentIndex(name){
  return {
    "Trend Agent":0,"Script Agent":1,"Visual Agent":2,"Voice Agent":3,
    "Character Agent":4,"Video Agent":5,"Analytics Agent":6,"Learning Agent":7
  }[name];
}
async function poll(){
  try{
    const res=await fetch("/agent-tasks?x="+Date.now());
    const data=await res.json();
    if(data.length>lastCount){
      data.slice(lastCount).forEach(t=>{
        const i=agentIndex(t.agent);
        if(i!==undefined)activateAgent(i);
        if(t.agent==="Jarvis")statusBox.innerText=t.detail;
      });
      lastCount=data.length;
    }
    document.getElementById("tasks").innerHTML=data.slice(-10).map(t=>
      `<div>[${t.time}] <b>${t.agent}</b> — ${t.status}: ${t.detail}</div>`
    ).join("");
  }catch(e){}
}
async function send(){
  const input=document.getElementById("text");
  const text=input.value;
  input.value="";
  await fetch("/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});
}
document.getElementById("text").addEventListener("keydown",e=>{if(e.key==="Enter")send()});
setInterval(poll,800);
poll();
</script>
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