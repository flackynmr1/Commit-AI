def listen_once(seconds=4):
    fs = 16000
    filename = "voice.wav"

    print("Lyssnar med mic:", MIC_DEVICE)

    try:
        audio = sd.rec(
            int(seconds * fs),
            samplerate=fs,
            channels=1,
            dtype="int16",
            device=MIC_DEVICE
        )
        sd.wait()

    except Exception as e:
        print("MIC FEL:", e)
        time.sleep(1)
        return ""

    write(filename, fs, audio)

    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        data = recognizer.record(source)

    try:
        return recognizer.recognize_google(data, language="sv-SE").lower()
    except:
        try:
            return recognizer.recognize_google(data, language="en-US").lower()
        except:
            return ""