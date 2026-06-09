import re
from urllib.request import Request, urlopen
from html.parser import HTMLParser


def clean(value, fallback=""):
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value if value else fallback


def fix_text(text):
    text = clean(text)
    fixes = {
        "hemsdior": "hemsidor",
        "mer kunder": "fler kunder",
        "få mer": "få fler",
        "ai": "AI",
        "mail": "mejl",
        "steavfel": "stavfel",
        "service bolag": "servicebolag",
    }
    for wrong, right in fixes.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text, flags=re.IGNORECASE)
    return text


def build_ai_profile(raw):
    service_type = clean(raw.get("service_type"), "other")
    return {
        "sender_name": fix_text(raw.get("sender_name", "")),
        "company_name": fix_text(raw.get("company_name", "")),
        "service_type": service_type,
        "offer": fix_text(raw.get("offer", "")),
        "problem_solved": fix_text(raw.get("problem_solved", "")),
        "target_customer": fix_text(raw.get("target_customer", "")),
        "customer_result": fix_text(raw.get("customer_result", "")),
        "proof": fix_text(raw.get("proof", "")),
        "phone": clean(raw.get("phone", "")),
        "website": clean(raw.get("website", "")),
        "tone": clean(raw.get("tone", "professionell, enkel och inte för säljig")),
    }


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "noscript"]:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ["script", "style", "noscript"]:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            d = clean(data)
            if d:
                self.parts.append(d)


def fetch_website_text(url, limit=2500):
    url = clean(url)
    if not url:
        return ""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=5) as res:
            html = res.read().decode("utf-8", errors="ignore")
        ex = Extractor()
        ex.feed(html)
        return clean(" ".join(ex.parts))[:limit]
    except Exception:
        return ""


SERVICE_KEYWORDS = {
    "website": ["hemsida", "webb", "landningssida", "design", "konvertering", "offert", "kontakt"],
    "seo": ["google", "seo", "synlighet", "sök", "lokal", "ranking"],
    "ads": ["annonser", "google ads", "meta ads", "kampanj", "trafik", "kunder"],
    "leadgen": ["leads", "kundförfrågningar", "möten", "prospekt", "försäljning"],
    "ai_chatbot": ["svar", "kundservice", "bokning", "chatbot", "receptionist", "kontakt"],
    "marketing": ["marknadsföring", "synlighet", "sociala medier", "kampanj", "varumärke"],
    "vvs": ["vvs", "rör", "installation", "värme", "vatten", "avlopp", "entreprenad"],
    "other": [],
}

INDUSTRY_KEYWORDS = {
    "flytt_stad": ["flytt", "städ", "flyttfirma", "städfirma"],
    "bygg": ["bygg", "tak", "snick", "måleri", "renovering"],
    "vvs": ["vvs", "rör", "värme", "avlopp", "installation"],
    "salong": ["salong", "frisör", "klinik", "massage", "skönhet"],
    "restaurang": ["restaurang", "cafe", "café", "bar", "mat"],
    "professional": ["redovisning", "juridik", "konsult", "byrå"],
}


def detect_industry_group(industry, website_text=""):
    text = f"{industry} {website_text}".lower()
    for group, words in INDUSTRY_KEYWORDS.items():
        if any(w in text for w in words):
            return group
    return "general"


def detect_service_type(profile):
    service_type = clean(profile.get("service_type", "other")).lower()
    raw = " ".join([
        clean(profile.get("offer", "")),
        clean(profile.get("problem_solved", "")),
        clean(profile.get("target_customer", "")),
        clean(profile.get("customer_result", "")),
    ]).lower()

    if service_type and service_type != "other":
        return service_type

    scores = {}
    for stype, words in SERVICE_KEYWORDS.items():
        scores[stype] = sum(1 for w in words if w in raw)

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"


def calculate_match(service_type, industry_group, website_text, profile):
    score = 40
    reasons = []
    warnings = []

    service_to_good_industries = {
        "website": ["flytt_stad", "bygg", "vvs", "salong", "restaurang", "professional", "general"],
        "seo": ["flytt_stad", "bygg", "vvs", "salong", "restaurang", "professional", "general"],
        "ads": ["flytt_stad", "salong", "restaurang", "professional", "general"],
        "leadgen": ["bygg", "vvs", "professional", "general"],
        "ai_chatbot": ["flytt_stad", "salong", "professional", "general"],
        "marketing": ["flytt_stad", "salong", "restaurang", "professional", "general"],
        "vvs": ["vvs", "bygg"],
        "other": ["general"],
    }

    if industry_group in service_to_good_industries.get(service_type, []):
        score += 35
        reasons.append("tjänsten matchar leadens bransch")
    else:
        score -= 20
        warnings.append("tjänsten verkar inte matcha leadens bransch särskilt bra")

    if website_text:
        score += 12
        reasons.append("det finns information online att anpassa pitchen efter")

    raw_target = clean(profile.get("target_customer", "")).lower()
    if industry_group != "general" and any(w in raw_target for w in INDUSTRY_KEYWORDS.get(industry_group, [])):
        score += 18
        reasons.append("leadens bransch finns i din målgrupp")

    if service_type == "vvs" and industry_group == "flytt_stad":
        score = min(score, 35)
        warnings.append("flytt/städ är inte en tydlig köpare av VVS-tjänster")

    return max(0, min(score, 98)), reasons[:4], warnings[:3]


def get_relevance_angle(service_type, industry_group):
    if service_type == "website":
        return {
            "problem": "kunder ofta jämför flera företag innan de bestämmer sig",
            "value": "göra hemsidan tydligare, bygga mer förtroende och få fler besökare att ta kontakt",
            "angle": "fler offertförfrågningar via hemsidan",
        }

    if service_type == "seo":
        return {
            "problem": "många kunder söker lokalt på Google innan de väljer företag",
            "value": "synas bättre när kunder söker efter era tjänster",
            "angle": "bättre lokal synlighet",
        }

    if service_type == "ads":
        return {
            "problem": "det kan vara svårt att få ett jämnt inflöde av nya kunder",
            "value": "driva mer relevant trafik och fler förfrågningar",
            "angle": "fler kunder via annonsering",
        }

    if service_type == "ai_chatbot":
        return {
            "problem": "förfrågningar ofta tappas när kunder inte får svar snabbt",
            "value": "svara snabbare, samla in kontaktuppgifter och boka fler samtal",
            "angle": "snabbare kundrespons",
        }

    if service_type == "vvs":
        return {
            "problem": "projekt ofta kräver rätt kompetens, snabb planering och pålitliga samarbeten",
            "value": "hjälpa med VVS-installationer, projektstöd eller samarbeten där rätt kompetens behövs",
            "angle": "VVS-stöd och samarbeten",
        }

    return {
        "problem": "det kan vara svårt att få rätt kundkontakt utan tydlig positionering",
        "value": "skapa tydligare första kontakt och bättre matchning",
        "angle": "relevant samarbete",
    }


def analyze_lead(lead, profile):
    company = clean(getattr(lead, "company_name", ""), "företaget")
    industry = clean(getattr(lead, "industry", ""), "er bransch")
    city = clean(getattr(lead, "city", ""))
    website = clean(getattr(lead, "website", ""))

    website_text = fetch_website_text(website)
    service_type = detect_service_type(profile)
    industry_group = detect_industry_group(industry, website_text)

    match_score, reasons, warnings = calculate_match(
        service_type=service_type,
        industry_group=industry_group,
        website_text=website_text,
        profile=profile,
    )

    angle = get_relevance_angle(service_type, industry_group)

    if website_text:
        insight = f"Jag såg att ni arbetar med {industry.lower()} och har information online där kunder kan läsa mer om era tjänster."
    elif city:
        insight = f"Jag såg att ni är verksamma inom {industry.lower()} i {city}."
    else:
        insight = f"Jag såg att ni arbetar inom {industry.lower()}."

    return {
        "company": company,
        "industry": industry,
        "city": city,
        "service_type": service_type,
        "industry_group": industry_group,
        "match_score": match_score,
        "is_relevant": match_score >= 55,
        "reasons": reasons,
        "warnings": warnings,
        "insight": insight,
        "problem": angle["problem"],
        "value": angle["value"],
        "angle": angle["angle"],
    }
