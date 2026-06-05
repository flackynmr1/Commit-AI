from free_video_agent import create_ai_business_video


def handle_command(command: str):
    command = command.lower().strip()

    if "skapa video" in command or "gör video" in command or "business video" in command:
        idea = command

        for remove in [
            "jarvis",
            "skapa video om",
            "skapa video",
            "gör video om",
            "gör video",
            "business video om",
            "business video",
        ]:
            idea = idea.replace(remove, "")

        idea = idea.strip()

        if not idea:
            idea = input("Vad ska videon handla om? ")

        video_path = create_ai_business_video(idea)
        print(f"Video klar: {video_path}")
        return

    if command in ["exit", "quit", "stäng"]:
        print("Stänger Jarvis.")
        raise SystemExit

    print("Jag förstod inte. Testa: skapa video om en app som hjälper företag få leads")


def main():
    print("Jarvis Free AI Video System startat.")
    print("Skriv t.ex: skapa video om en app som hjälper företag få leads")
    print("Skriv exit för att stänga.\n")

    while True:
        command = input("Du: ")
        handle_command(command)


if __name__ == "__main__":
    main()
