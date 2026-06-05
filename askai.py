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

        if "facts" not in memory:
            memory["facts"] = []

        if "history" not in memory:
            memory["history"] = []

        return memory

    except:
        save_memory(default)
        return default


def save_memory(memory):

    if "facts" not in memory:
        memory["facts"] = []

    if "history" not in memory:
        memory["history"] = []

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def remember(text):

    memory = load_memory()

    memory["facts"].append({
        "text": text,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    save_memory(memory)

    return "Jag kommer ihåg det."


def ask_ai(user_text):

    memory = load_memory()

    facts = "\n".join([
        f"- {x.get('text', '')}"
        for x in memory["facts"][-20:]
    ])

    history = "\n".join([
        f"User: {h.get('user', '')}\nJarvis: {h.get('ai', '')}"
        for h in memory["history"][-8:]
    ])

    prompt = f"""
Du är Jarvis, en svensk AI-assistent.

Prata naturlig modern svenska.
Var snabb, smart och praktisk.
Låtsas aldrig att du gör saker.
Var lite futuristisk och självsäker.

Du hjälper med:
- automation
- business
- kod
- musik
- videos
- productivity

Svara kort och naturligt.

Minne:
{facts}

Tidigare konversation:
{history}

User: {user_text}

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
                    "temperature": 0.6,
                    "num_predict": 180
                }
            },
            timeout=60
        )

        answer = r.json().get("response", "").strip()

        if not answer:
            answer = "Jag fick inget svar från modellen."

    except Exception as e:

        answer = f"AI-fel: {e}"

    memory["history"].append({
        "user": user_text,
        "ai": answer,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    memory["history"] = memory["history"][-50:]

    save_memory(memory)

    return answer