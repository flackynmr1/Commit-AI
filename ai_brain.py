import requests

def ask_ai(prompt):

    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        return r.json()["response"]
    except:
        return None