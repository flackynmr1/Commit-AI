import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json

model = Model("model")
rec = KaldiRecognizer(model, 16000)

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))


def listen_for_wake():
    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                           dtype="int16", channels=1, callback=callback):

        print("🎤 Listening for 'jarvis'...")

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")

                if text:
                    print("HEARD:", text)

                    if "jarvis" in text:
                        return True