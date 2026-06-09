import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen


def clean(value, fallback=""):
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value if value else fallback


def fix_text(text):
    text = clean(text)

    fixes = {
        "hemsdior": "hemsidor",
        "hemsidorr": "hemsidor",
        "mer kunder": "fler kunder",
        "få mer": "få fler",
        "företagare få": "företagare att få",
        "ai": "AI",
        "mail": "mejl",
        "mejls": "mejl",
        "buisness": "business",
        "marknadsföringg": "marknadsföring",
    }

    for wrong, right in fixes.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text, flags=re.IGNORECASE)

    return text


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "noscript"]:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ["script", "style", "noscript"]:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            data = clean(data)
            if data:
                self.parts.append(data)


def fetch_website_text(url, limit=3500):
    url = clean(url)
    if not url:
        return ""

    if not url.startswith("http"):
        url = "https://" + url

    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=6) as res:
            html = res.read().decode("utf-8", errors="ignore")

        parser = TextExtractor()
        parser.feed(html)
        text = clean(" ".join(parser.parts))
        return text[:limit]
    except Exception:
        return ""


def detect_business_signals(text):
    t = text.lower()
    signals = []

    checks = [
        ("offert", "de verkar arbeta med offertförfrågningar"),
        ("boka", "de verkar kunna få fler bokningar"),
        ("kontakt", "kontaktvägar finns, men kan ofta göras tydligare"),
        ("akut", "de verkar ha akuta kundärenden där snabb respons är viktig"),
        ("gratis konsultation", "de använder konsultationer som säljväg"),
        ("recension", "förtroende och omdömen verkar vara viktiga"),
        ("portfolio", "de visar tidigare arbete, vilket kan användas i säljflödet"),
        ("tjänster", "de har flera tjänster som kan paketeras tydligare"),
    ]

    for key, msg in checks:
        if key in t:
            signals.append(msg)

    return signals[:3]


def detect_industry_angle(industry, website_text, offer):
    combined = f"{industry} {website_text} {offer}".lower()

    if any(x in combined for x in ["bygg", "tak", "snick", "måleri", "vvs", "renovering"]):
        return {
            "category": "offert",
            "problem": "många kunder jämför flera företag innan de ber om offert",
            "value": "få in fler kvalificerade offertförfrågningar och följa upp dem snabbare",
        }

    if any(x in combined for x in ["städ", "flytt", "service", "hemservice"]):
        return {
            "category": "lokal service",
            "problem": "lokala servicebolag tappar ofta kunder när uppföljningen inte sker snabbt nog",
            "value": "hitta fler lokala kunder och skapa ett tydligare kontaktflöde",
        }

    if any(x in combined for x in ["salong", "frisör", "klinik", "massage", "skönhet", "spa"]):
        return {
            "category": "bokning",
            "problem": "bokningar avgörs ofta av tydlig information och snabb kontakt",
            "value": "få fler bokningsförfrågningar och bättre uppföljning",
        }

    if any(x in combined for x in ["restaurang", "café", "cafe", "bar", "mat"]):
        return {
            "category": "lokal synlighet",
            "problem": "restauranger behöver vara enkla att hitta och välja lokalt",
            "value": "öka lokal synlighet och skapa fler besök eller bokningar",
        }

    if any(x in combined for x in ["redovisning", "juridik", "konsult", "byrå", "agentur"]):
        return {
            "category": "förtroende",
            "problem": "tjänsteföretag behöver bygga förtroende tidigt i kundresan",
            "value": "hitta mer relevanta leads och skapa mer personliga första kontakter",
        }

    return {
        "category": "leadgenerering",
        "problem": "många företag lägger tid på manuell kundjakt utan tydlig struktur",
        "value": "hitta fler relevanta leads och skapa bättre första kontakt",
    }


def analyze_lead(lead, profile):
    company = clean(getattr(lead, "company_name", ""), "företaget")
    industry = clean(getattr(lead, "industry", ""), "branschen")
    city = clean(getattr(lead, "city", ""))
    website = clean(getattr(lead, "website", ""))

    offer = fix_text(profile.get("offer", "hjälpa företag att få fler kunder"))
    target = fix_text(profile.get("target_customer", "företag som vill växa"))

    website_text = fetch_website_text(website)
    signals = detect_business_signals(website_text)
    angle = detect_industry_angle(industry, website_text, offer)

    score = 55
    reasons = []

    if website:
        score += 10
        reasons.append("de har en digital närvaro som går att analysera")

    if website_text:
        score += 15
        reasons.append("hemsidan visar tydligt vad de arbetar med")

    if city:
        score += 5
        reasons.append(f"de är lokalt relevanta i {city}")

    if signals:
        score += 10
        reasons.extend(signals[:2])

    if industry:
        score += 8
        reasons.append(f"branschen matchar en tydlig pitch-vinkel: {angle['category']}")

    score = min(score, 96)

    if website_text:
        company_insight = f"Jag såg att ni verkar arbeta aktivt med {industry.lower()} och redan har information online som kunder kan utgå från."
    elif city:
        company_insight = f"Jag såg att ni är verksamma inom {industry.lower()} i {city}, vilket gjorde er relevanta att titta närmare på."
    else:
        company_insight = f"Jag såg att ni arbetar inom {industry.lower()}, vilket gjorde er relevanta att kontakta."

    if signals:
        personal_observation = signals[0].capitalize() + "."
    else:
        personal_observation = f"För företag inom {industry.lower()} är första kontakten ofta avgörande för att få in fler kundförfrågningar."

    return {
        "score": score,
        "company_insight": company_insight,
        "personal_observation": personal_observation,
        "problem": angle["problem"],
        "value": angle["value"],
        "reasons": reasons[:4],
        "offer": offer,
        "target_customer": target,
        "website_text_found": bool(website_text),
    }
