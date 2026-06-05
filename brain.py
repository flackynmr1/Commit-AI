from ai_brain import ask_ai

def brain(user_input):

    prompt = f"""
You are Jarvis, an AI assistant.
You are smart, short, and helpful.

User: {user_input}
Jarvis:
"""

    return ask_ai(prompt)