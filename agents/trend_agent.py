import random

IDEAS = [
    "local business website redesign side hustle",
    "AI content agency for restaurants",
    "short form content agency for real estate agents",
    "AI landing page business",
    "boring business that makes money",
    "small business automation service",
    "AI product video agency",
    "website before and after business idea"
]

def get_viral_idea():
    idea = random.choice(IDEAS)
    return {
        "source_title": idea,
        "idea": idea
    }