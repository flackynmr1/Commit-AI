# =========================
# askai.py
# =========================

import json
import os
import requests
from datetime import datetime

MEMORY_FILE = "memory.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"


def load_memory():

    default = {
        "facts": [],
        "history": []
    }

    if not os.path.exists(MEMORY_FILE):
        save_memory(default)
        return default

    try:

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)

        memory.setdefault("facts", [])
        memory.setdefault("history", [])

        return memory

    except:
        save_memory(default)
        return default


def save_memory(memory):

    memory.setdefault("facts", [])
    memory.setdefault("history", [])

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def remember(text):

    memory = load_memory()

    memory["facts"].append({
        "text": text,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    save_memory(memory)

    return "Jag kommer ihåg det bror."


def ask_ai(user_text):

    memory = load_memory()

    facts = "\n".join([
        f"- {x.get('text', '')}"
        for x in memory["facts"][-20:]
    ])

    history = "\n".join([
        f"Elias: {h.get('user', '')}\nJarvis: {h.get('ai', '')}"
        for h in memory["history"][-6:]
    ])

    prompt = f"""
Du är Jarvis, Elias personliga AI-assistent.

Stil:
- prata som en smart polare
- säg ibland "bror" eller "cuz"
- svara kort
- max 1-2 meningar
- inga långa listor
- naturlig modern svenska
- låt inte som en robot
- var snabb, chill och användbar
- om du inte fattar, säg:
"Jag hörde inte riktigt bror, säg igen."

Minne:
{facts}

Senaste:
{history}

Elias: {user_text}

Jarvis:
"""

    try:

        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 60
                }
            },
            timeout=35
        )

        answer = r.json().get("response", "").strip()

        if not answer:
            answer = "Jag fick inget svar från modellen bror."

    except Exception as e:

        answer = f"AI-fel: {e}"

    if "." in answer:
        answer = answer.split(".")[0] + "."

    if len(answer) > 120:
        answer = answer[:120] + "..."

    memory["history"].append({
        "user": user_text,
        "ai": answer,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    memory["history"] = memory["history"][-40:]

    save_memory(memory)

    return answer