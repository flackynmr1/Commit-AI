def clean(value, fallback=""):
    if value is None:
        return fallback
    value = str(value).strip()
    return value if value else fallback


def lower(value):
    return clean(value).lower()


SERVICE_RULES = {
    "flytt": {
        "keywords": ["flytt", "transport", "bortforsling", "magasinering", "kontorsflytt"],
        "targets": {
            "fastighetsbolag": "fastighetsbolag hanterar lokaler, hyresgäster och flyttar oftare än många andra företag",
            "mäklare": "mäklare möter kunder som ofta är mitt i en flyttprocess",
            "kontor": "kontor kan behöva hjälp med kontorsflyttar, möbler och transport",
            "coworking": "coworking-miljöer har ofta företag som växer, byter plats eller behöver flytthjälp",
            "bygg": "byggföretag kan behöva transport, bortforsling och materialflytt",
            "lager": "lager och logistikverksamheter har ofta transport- och flyttbehov",
            "butik": "butiker kan behöva hjälp med leveranser, ommöblering eller flytt",
        },
        "angle": "flytt, transport och bortforsling",
        "cta": "vill ni att jag skickar över ett kort exempel på hur vi kan hjälpa vid nästa flytt eller transport?",
    },

    "stad": {
        "keywords": ["städ", "städfirma", "lokalvård", "rengöring", "kontorsstäd"],
        "targets": {
            "kontor": "kontor behöver ofta löpande städning för att hålla arbetsmiljön fräsch",
            "restaurang": "restauranger har höga krav på renlighet och regelbunden städning",
            "hotell": "hotell är beroende av renlighet och återkommande städflöden",
            "gym": "gym behöver ofta frekvent städning på grund av många dagliga besökare",
            "klinik": "kliniker behöver en ren och trygg miljö för kunder och personal",
            "salong": "salonger behöver hålla lokalerna rena och representativa varje dag",
            "fastighetsbolag": "fastighetsbolag behöver ofta trappstädning, flyttstädning och lokalvård",
        },
        "angle": "städning och lokalvård",
        "cta": "vill ni att jag skickar över ett kort upplägg för hur vi kan hjälpa med städningen?",
    },

    "webb": {
        "keywords": ["webb", "hemsida", "webbyrå", "seo", "design", "digital närvaro"],
        "targets": {
            "restaurang": "restauranger vinner ofta kunder genom en tydlig hemsida, meny och bokningsflöde",
            "bygg": "byggföretag kan få fler offertförfrågningar med en tydlig hemsida och lokalt SEO",
            "vvs": "VVS-företag kan få fler akuta och lokala förfrågningar via en bättre hemsida",
            "salong": "salonger får ofta fler bokningar när tjänster, priser och kontaktvägar är tydliga",
            "klinik": "kliniker behöver förtroende, tydlig information och smidiga bokningsvägar online",
            "butik": "butiker kan öka besök och förfrågningar med bättre digital synlighet",
            "gym": "gym kan få fler provträningar och leads med bättre landningssidor",
        },
        "angle": "hemsida, SEO och fler kundförfrågningar",
        "cta": "vill ni att jag skickar ett kort exempel på vad som skulle kunna förbättras digitalt?",
    },

    "marketing": {
        "keywords": ["marketing", "marknadsföring", "annonser", "leads", "reklam", "sociala medier"],
        "targets": {
            "restaurang": "restauranger kan få fler bokningar med bättre annonser och lokal synlighet",
            "salong": "salonger kan fylla kalendern med lokala kampanjer och återkommande kunder",
            "gym": "gym kan få fler provträningar genom lokala kampanjer",
            "bygg": "byggföretag kan få fler offertförfrågningar med rätt leadflöde",
            "vvs": "VVS-företag kan få fler lokala förfrågningar när kunder söker akut hjälp",
            "klinik": "kliniker kan få fler bokningar genom tydligare erbjudanden och annonser",
            "butik": "butiker kan driva fler besök och köp med lokal marknadsföring",
        },
        "angle": "marknadsföring och leadgenerering",
        "cta": "vill ni att jag skickar över ett kort förslag på hur ni kan få fler förfrågningar?",
    },

    "foto": {
        "keywords": ["foto", "fotograf", "video", "content", "bilder", "film"],
        "targets": {
            "restaurang": "restauranger säljer mycket på bra bilder av mat, lokal och känsla",
            "hotell": "hotell behöver starka bilder för att bygga förtroende och få fler bokningar",
            "mäklare": "mäklare är beroende av bra bilder för att skapa intresse",
            "salong": "salonger kan visa resultat, miljö och känsla med bättre content",
            "gym": "gym kan få fler leads med starkt video- och bildmaterial",
            "butik": "butiker kan lyfta produkter och kampanjer med bättre content",
        },
        "angle": "foto, video och content",
        "cta": "vill ni att jag skickar över ett kort exempel på content som skulle passa er?",
    },
}


def detect_service_category(profile):
    text = lower(
        " ".join([
            clean(profile.get("company_name")),
            clean(profile.get("offer")),
            clean(profile.get("target_customer")),
            clean(profile.get("proof")),
        ])
    )

    for category, data in SERVICE_RULES.items():
        for keyword in data["keywords"]:
            if keyword in text:
                return category

    return "general"


def lead_text(lead):
    return lower(
        " ".join([
            clean(getattr(lead, "company_name", "")),
            clean(getattr(lead, "industry", "")),
            clean(getattr(lead, "city", "")),
            clean(getattr(lead, "website", "")),
            clean(getattr(lead, "source", "")),
        ])
    )


def get_lead_industry(lead):
    return lower(getattr(lead, "industry", ""))


def score_lead_relevance(lead, profile):
    category = detect_service_category(profile)
    text = lead_text(lead)
    industry = get_lead_industry(lead)

    company_name = clean(profile.get("company_name"), "ert företag")
    offer = clean(profile.get("offer"), "våra tjänster")
    target_customer = clean(profile.get("target_customer"), "företag")

    if category == "general":
        return {
            "score": 55,
            "category": "general",
            "is_relevant": True,
            "angle": offer,
            "reason": f"ni matchar målgruppen som {company_name} vill nå",
            "matched_target": target_customer,
            "cta": "vill ni att jag skickar över lite mer information?",
        }

    rules = SERVICE_RULES[category]

    best_match = None
    best_reason = None
    score = 25

    for target, reason in rules["targets"].items():
        if target in text or target in industry:
            best_match = target
            best_reason = reason
            score = 90
            break

    if not best_match:
        score = 45
        best_match = industry or "företag"
        best_reason = (
            f"ni kan passa målgruppen för {company_name}, men matchningen är inte helt säker"
        )

    return {
        "score": score,
        "category": category,
        "is_relevant": score >= 60,
        "angle": rules["angle"],
        "reason": best_reason,
        "matched_target": best_match,
        "cta": rules["cta"],
    }


def build_relevance_sentence(lead, profile):
    relevance = score_lead_relevance(lead, profile)

    company = clean(getattr(lead, "company_name", ""), "ert företag")
    industry = clean(getattr(lead, "industry", ""), "er bransch")
    city = clean(getattr(lead, "city", ""), "Sverige")

    if relevance["is_relevant"]:
        return (
            f"Jag såg att {company} arbetar inom {industry} i {city}. "
            f"Anledningen till att jag kontaktar er är att {relevance['reason']}."
        )

    return (
        f"Jag såg att {company} arbetar inom {industry} i {city}. "
        f"Jag är inte helt säker på om timingen är rätt, men jag ville ändå höra om "
        f"{relevance['angle']} kan vara relevant för er framöver."
    )


def build_pitch_angle(lead, profile):
    relevance = score_lead_relevance(lead, profile)
    return relevance["angle"]


def build_cta(lead, profile):
    relevance = score_lead_relevance(lead, profile)
    return relevance["cta"]


def is_relevant_lead(lead, profile, min_score=60):
    return score_lead_relevance(lead, profile)["score"] >= min_score