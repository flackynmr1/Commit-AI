import random

def make_script(trend):
    hooks = [
        "Bro, this business idea is actually genius.",
        "Nobody talks about this boring business idea.",
        "If I had to start from zero, I would do this.",
        "This is not sexy, but it can make money.",
        "Here is a simple AI business idea."
    ]

    businesses = [
        "Find local businesses with terrible websites, remake them with AI, and charge three hundred dollars.",
        "Find restaurants with weak social media, make them short videos, and sell a monthly content package.",
        "Find real estate agents with boring posts, create thirty days of content, and charge a setup fee.",
        "Find barbers, gyms, and cleaners with no landing page, build one fast, and sell the upgrade.",
        "Create before and after product videos for small online stores, then charge per video."
    ]

    hook = random.choice(hooks)
    business = random.choice(businesses)

    script_lines = [
        hook,
        business,
        "Step one, find a boring business with bad marketing.",
        "Step two, make their website or content look ten times better.",
        "Step three, send them a simple before and after.",
        "Most people chase fancy ideas.",
        "Smart people solve boring problems and get paid.",
        "Follow for more business ideas."
    ]

    title = "This business idea is actually genius #Shorts"
    description = "#business #startup #sidehustle #money #ai #entrepreneur #shorts"

    return title, script_lines, description