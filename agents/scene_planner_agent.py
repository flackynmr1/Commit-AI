def plan_scenes(script_lines):
    scenes = []

    for line in script_lines:
        t = line.lower()

        if "website" in t or "landing page" in t or "redesign" in t:
            scenes.append({"type": "website_before_after", "line": line})
        elif "ai" in t or "automation" in t:
            scenes.append({"type": "ai_dashboard", "line": line})
        elif "send" in t or "client" in t or "owner" in t:
            scenes.append({"type": "client_email", "line": line})
        elif "charge" in t or "paid" in t or "money" in t or "dollars" in t:
            scenes.append({"type": "payment", "line": line})
        elif "social media" in t or "content" in t or "videos" in t or "posts" in t:
            scenes.append({"type": "content_calendar", "line": line})
        elif "problem" in t or "boring" in t or "bad marketing" in t:
            scenes.append({"type": "problem_list", "line": line})
        else:
            scenes.append({"type": "business_laptop", "line": line})

    return scenes