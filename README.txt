JARVIS FREE AI VIDEO SYSTEM
===========================

100% gratis lokalt system för att skapa AI-förklaringsvideos.

Vad det gör:
1. Du skriver eller säger en business-idé.
2. Systemet skapar ett enkelt manus lokalt.
3. Edge TTS skapar svensk röst gratis.
4. MoviePy gör en MP4-video med text/slides + röst.
5. Om du senare installerar SadTalker kan systemet även göra avatar-video.

INSTALLATION
------------

Öppna PowerShell i din JARVIS-mapp:

    cd C:\Users\46730\Desktop\JARVIS

Aktivera venv:

    .\venv\Scripts\activate

Installera paket:

    pip install edge-tts moviepy pillow requests

Om moviepy strular, kör:

    pip install moviepy==1.0.3

Lägg filerna i din JARVIS-mapp.

KÖR
---

Testa skapa video:

    python free_video_agent.py

Eller kör Jarvis:

    python main.py

Säg eller skriv:

    skapa video om min business idea

Videos sparas i:

    videos/

VIKTIGT
-------

Detta är 100% gratis och lokalt, men det är inte exakt lika proffsigt som HeyGen direkt.
Gratis HeyGen-liknande avatar kräver SadTalker/Wav2Lip installerat separat.

SadTalker-läge:
- Lägg SadTalker i:
  C:\Users\46730\Desktop\JARVIS\SadTalker
- Lägg en avatarbild som:
  assets\avatar.png
- Systemet försöker då köra avatar-video automatiskt.
