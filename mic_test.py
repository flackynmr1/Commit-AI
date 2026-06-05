import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr

print("Mikrofoner:")
print(sd.query_devices())

fs = 16000
seconds = 5

print("Prata nu i 5 sekunder...")
audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype="int16")
sd.wait()

write("test.wav", fs, audio)

r = sr.Recognizer()

with sr.AudioFile("test.wav") as source:
    data = r.record(source)

try:
    text = r.recognize_google(data, language="sv-SE")
    print("HÖRDE:", text)
except Exception as e:
    print("FEL:", e)