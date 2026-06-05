import webbrowser
import os
import pyautogui
import time

def handle_desktop(command):

    c = command.lower()

    # 🌐 web
    if "youtube" in c:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube"

    if "google" in c:
        import os

os.system("xdg-open https://google.com")

    # 💻 apps
    if "steam" in c:
        os.startfile("steam://open/main")
        return "Opening Steam"

    # 🖱 control examples
    if "minimera" in c:
        pyautogui.hotkey("win", "down")
        return "Minimizing window"

    if "skriv hej" in c:
        pyautogui.write("hej")
        return "Typing"

    return None