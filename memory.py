import json
import os

MEMORY_FILE = "memory.json"


# -----------------------------
# LOAD MEMORY
# -----------------------------
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# -----------------------------
# SAVE MEMORY
# -----------------------------
def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# CLEAR MEMORY (OPTIONAL)
# -----------------------------
def clear_memory():
    save_memory({})