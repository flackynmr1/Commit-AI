import os
from PIL import Image, ImageDraw, ImageFont
from agents.scene_planner_agent import plan_scenes

W, H = 760, 560
BOLD = "C:/Windows/Fonts/arialbd.ttf"
REG = "C:/Windows/Fonts/arial.ttf"

def f(path, size):
    return ImageFont.truetype(path, size)

def base():
    img = Image.new("RGB", (W, H), (10, 12, 22))
    d = ImageDraw.Draw(img)
    d.ellipse([-140, -120, 340, 360], fill=(30, 42, 90))
    d.ellipse([420, 220, 920, 720], fill=(42, 28, 80))
    return img, d

def save(img, i):
    os.makedirs("content_factory/assets/mockups", exist_ok=True)
    path = f"content_factory/assets/mockups/scene_{i}.jpg"
    img.save(path, quality=94)
    return path

def website_before_after(i):
    img, d = base()
    d.text((165, 25), "BEFORE  →  AFTER", font=f(BOLD, 42), fill=(255,255,255))

    d.rounded_rectangle([45, 105, 350, 445], radius=24, fill=(235,235,235))
    d.rectangle([75, 140, 320, 190], fill=(185,45,45))
    d.rectangle([75, 225, 310, 260], fill=(180,180,180))
    d.rectangle([75, 295, 270, 395], fill=(160,160,160))
    d.text((110, 465), "OLD SITE", font=f(BOLD, 28), fill=(255,255,255))

    d.rounded_rectangle([410, 105, 715, 445], radius=24, fill=(13,20,38))
    d.rounded_rectangle([445, 145, 680, 230], radius=18, fill=(75,120,255))
    d.rounded_rectangle([445, 280, 555, 395], radius=16, fill=(255,255,255))
    d.rounded_rectangle([575, 280, 680, 395], radius=16, fill=(60,220,150))
    d.text((465, 465), "NEW SITE", font=f(BOLD, 28), fill=(255,255,255))
    return save(img, i)

def ai_dashboard(i):
    img, d = base()
    d.text((210, 25), "AI BUILDS IT", font=f(BOLD, 46), fill=(255,255,255))
    d.rounded_rectangle([70, 115, 690, 455], radius=30, fill=(8,10,20), outline=(95,130,255), width=6)

    for y in [165, 225, 285, 345]:
        d.rounded_rectangle([120, y, 640, y+36], radius=12, fill=(35,45,80))
        d.rectangle([145, y+13, 335, y+22], fill=(120,170,255))
        d.rectangle([370, y+13, 610, y+22], fill=(80,220,150))

    d.ellipse([320, 385, 440, 505], fill=(75,120,255))
    d.text((355, 415), "AI", font=f(BOLD, 36), fill=(255,255,255))
    return save(img, i)

def client_email(i):
    img, d = base()
    d.text((145, 25), "SEND THE RESULT", font=f(BOLD, 42), fill=(255,255,255))

    d.rounded_rectangle([75, 105, 685, 470], radius=28, fill=(245,245,245))
    d.rectangle([75, 105, 685, 160], fill=(40,80,180))
    d.text((110, 123), "Message to business owner", font=f(BOLD, 24), fill=(255,255,255))

    d.text((115, 215), "I redesigned your website.", font=f(REG, 28), fill=(30,30,30))
    d.text((115, 260), "Here is the before and after.", font=f(REG, 28), fill=(30,30,30))
    d.rounded_rectangle([115, 330, 330, 395], radius=18, fill=(210,60,60))
    d.rounded_rectangle([410, 330, 625, 395], radius=18, fill=(60,190,120))
    d.text((160, 350), "BEFORE", font=f(BOLD, 24), fill=(255,255,255))
    d.text((470, 350), "AFTER", font=f(BOLD, 24), fill=(255,255,255))
    return save(img, i)

def payment(i):
    img, d = base()
    d.text((270, 25), "GET PAID", font=f(BOLD, 50), fill=(255,255,255))
    d.rounded_rectangle([180, 115, 580, 455], radius=35, fill=(20,120,70))
    d.rounded_rectangle([235, 165, 525, 405], radius=22, fill=(245,245,245))
    d.text((270, 205), "INVOICE PAID", font=f(BOLD, 30), fill=(30,30,30))
    d.text((310, 270), "$300", font=f(BOLD, 70), fill=(20,120,70))
    d.text((275, 365), "Website redesign", font=f(REG, 24), fill=(60,60,60))
    return save(img, i)

def content_calendar(i):
    img, d = base()
    d.text((160, 25), "CONTENT SYSTEM", font=f(BOLD, 42), fill=(255,255,255))
    d.rounded_rectangle([60, 105, 700, 460], radius=28, fill=(245,245,245))

    days = ["MON", "TUE", "WED", "THU", "FRI"]
    x = 95
    for day in days:
        d.rounded_rectangle([x, 155, x+100, 390], radius=16, fill=(30,35,55))
        d.text((x+18, 178), day, font=f(BOLD, 20), fill=(255,255,255))
        for y in [230, 280, 330]:
            d.rectangle([x+18, y, x+82, y+18], fill=(90,150,255))
        x += 120
    return save(img, i)

def problem_list(i):
    img, d = base()
    d.text((120, 25), "BORING PROBLEMS PAY", font=f(BOLD, 38), fill=(255,255,255))
    d.rounded_rectangle([95, 110, 665, 455], radius=28, fill=(245,245,245))

    items = ["Bad website", "No social media", "Slow replies", "No landing page"]
    y = 160
    for item in items:
        d.text((150, y), "X", font=f(BOLD, 34), fill=(220,60,60))
        d.text((210, y+3), item, font=f(BOLD, 30), fill=(30,30,30))
        y += 70
    return save(img, i)

def business_laptop(i):
    img, d = base()
    d.text((120, 25), "SIMPLE BUSINESS IDEA", font=f(BOLD, 38), fill=(255,255,255))
    d.rounded_rectangle([110, 125, 650, 430], radius=30, fill=(30,35,50))
    d.rounded_rectangle([160, 170, 600, 365], radius=20, fill=(10,15,25))
    d.rectangle([205, 210, 555, 230], fill=(80,150,255))
    d.rectangle([205, 265, 510, 285], fill=(70,210,140))
    d.rectangle([205, 320, 545, 340], fill=(180,180,190))
    d.text((210, 455), "BUILD → SELL → REPEAT", font=f(BOLD, 28), fill=(255,255,255))
    return save(img, i)

def make_assets(script_lines):
    scenes = plan_scenes(script_lines)
    paths = []

    makers = {
        "website_before_after": website_before_after,
        "ai_dashboard": ai_dashboard,
        "client_email": client_email,
        "payment": payment,
        "content_calendar": content_calendar,
        "problem_list": problem_list,
        "business_laptop": business_laptop,
    }

    print("\n=== MOCKUP SCENE PLAN ===")
    for i, scene in enumerate(scenes, start=1):
        print(i, scene["type"])
        maker = makers.get(scene["type"], business_laptop)
        paths.append(maker(i))
    print("=========================\n")

    return paths