import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BOLD = "C:/Windows/Fonts/arialbd.ttf"
REG = "C:/Windows/Fonts/arial.ttf"

def create_character_image():
    os.makedirs("content_factory/assets", exist_ok=True)
    path = "content_factory/assets/cartoon_business_guy.png"

    img = Image.new("RGB", (W, H), (18, 20, 28))
    d = ImageDraw.Draw(img)

    d.ellipse([-280, 120, 480, 880], fill=(32, 40, 78))
    d.ellipse([690, 950, 1400, 1700], fill=(45, 35, 82))

    # Big UI screen frame
    d.rounded_rectangle([120, 520, 960, 1220], radius=48, fill=(5, 7, 12), outline=(255,255,255), width=8)
    d.rectangle([150, 550, 930, 610], fill=(25, 28, 42))

    # Character bottom-right
    d.ellipse([610, 1120, 910, 1420], fill=(245, 190, 140))
    d.rectangle([675, 1400, 845, 1700], fill=(45, 90, 160))
    d.ellipse([675, 1220, 725, 1270], fill=(255,255,255))
    d.ellipse([795, 1220, 845, 1270], fill=(255,255,255))
    d.ellipse([695, 1238, 718, 1260], fill=(0,0,0))
    d.ellipse([815, 1238, 838, 1260], fill=(0,0,0))
    d.arc([700, 1300, 830, 1370], 10, 170, fill=(80,20,20), width=8)

    # Desk
    d.rectangle([0, 1640, 1080, 1920], fill=(34, 28, 26))

    try:
        f = ImageFont.truetype(BOLD, 46)
        d.text((165, 555), "BUSINESS IDEA", font=f, fill=(255,255,255))
    except:
        pass

    img.save(path)
    return path