def wake_listener():
    global jarvis_awake, browser_opened

    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    mic = sr.Microphone()

    print("Kalibrerar mikrofon...")
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=2)

    print("LYSSNAR EFTER WAKE WORD: säg 'Jarvis' eller 'vakna'")

    while True:
        try:
            with mic as source:
                print("Lyssnar...")
                audio = r.listen(source, timeout=None, phrase_time_limit=4)

            try:
                text = r.recognize_google(audio, language="sv-SE").lower()
            except:
                text = r.recognize_google(audio, language="en-US").lower()

            print("HÖRDE:", text)

            if not jarvis_awake:
                if (
                    "jarvis" in text
                    or "vakna" in text
                    or "wake up" in text
                    or "wakeup" in text
                    or "hej jarvis" in text
                ):
                    jarvis_awake = True

                    if not browser_opened:
                        webbrowser.open(URL)
                        browser_opened = True

                    print("JARVIS VAKNADE")
                    speak("Jag är här. Vad vill du göra?")
                else:
                    print("Wake word hittades inte.")

            else:
                print("KOMMANDO:", text)

                answer = command(text)
                if not answer:
                    answer = ask_ai(text)

                print("SVAR:", answer)
                speak(answer)

        except sr.UnknownValueError:
            print("Jag hörde ljud men kunde inte tolka det.")
        except Exception as e:
            print("Fel i wake listener:", e)