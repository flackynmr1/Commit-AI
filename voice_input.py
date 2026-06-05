import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
import time

model = Model("model/vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

q = queue.Queue()

def callback(indata, frames, time_info, status):
    q.put(bytes(indata))


def listen_command():

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=callback
    ):

        print("🎤 Listening command...")

        timeout = 8  # ⬅️ viktigt

        start = time.time()

        while True:

            # 🛑 TIMEOUT (förhindrar freeze)
            if time.time() - start > timeout:
                return ""

            try:
                data = q.get(timeout=0.5)
            except:
                continue

            if rec.AcceptWaveform(data):

                result = json.loads(rec.Result())
                text = result.get("text", "").lower()

                if text != "":
                    print("USER:", text)
                    return text