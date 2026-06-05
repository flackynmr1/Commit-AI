import os
import webbrowser


# 🖥 OPEN APPS
def open_app(app):

    apps = {
        "chrome": "start chrome",
        "steam": "start steam",
        "discord": "start discord",
        "spotify": "start spotify",
        "explorer": "start explorer"
    }

    if app in apps:
        os.system(apps[app])
        return f"Öppnar {app}"

    return "App hittades inte"


# 🌐 OPEN WEBSITES
def open_website(url):
    webbrowser.open(url)
    return "Öppnar website"


# 🔊 SYSTEM CONTROL (basic desktop control)
def system_action(action):

    action = action.lower()

    # volume up (Windows)
    if "volume up" in action:
        os.system("powershell -c (New-Object -ComObject WScript.Shell).SendKeys([char]175)")
        return "Höjer volymen"

    # volume down
    if "volume down" in action:
        os.system("powershell -c (New-Object -ComObject WScript.Shell).SendKeys([char]174)")
        return "Sänker volymen"

    # mute
    if "mute" in action:
        os.system("powershell -c (New-Object -ComObject WScript.Shell).SendKeys([char]173)")
        return "Ljud av"

    return "Okänt systemkommando"