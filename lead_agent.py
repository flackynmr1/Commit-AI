def generate_demo_leads(city="Malmö", industry="flyttfirma"):
    city = city.strip().title()
    industry = industry.strip().lower()

    companies = [
        f"{city} {industry.title()} AB",
        f"Snabb {industry.title()} {city}",
        f"Nordic {industry.title()} Service",
        f"{industry.title()} Proffsen {city}",
        f"{city} Expert Service",
    ]

    leads = []

    for i, name in enumerate(companies, start=1):
        leads.append({
            "company_name": name,
            "industry": industry,
            "city": city,
            "website": f"https://example{i}.se",
            "phone": f"070-000 00 0{i}",
            "email": "",
            "source": "demo"
        })

    return leads