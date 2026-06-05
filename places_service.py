import os
import requests


def search_places(city="Malmö", industry="flyttfirma", limit=10):
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")

    if not api_key:
        print("Missing GOOGLE_PLACES_API_KEY")
        return []

    query = f"{industry} {city}"

    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    search_response = requests.get(
        search_url,
        params={
            "query": query,
            "key": api_key,
            "language": "sv",
            "region": "se",
        },
        timeout=20
    )

    search_response.raise_for_status()
    search_data = search_response.json()

    results = []

    for place in search_data.get("results", [])[:limit]:
        place_id = place.get("place_id")

        phone = ""
        website = ""

        if place_id:
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_response = requests.get(
                details_url,
                params={
                    "place_id": place_id,
                    "key": api_key,
                    "language": "sv",
                    "fields": "formatted_phone_number,website"
                },
                timeout=20
            )

            if details_response.ok:
                details_data = details_response.json().get("result", {})
                phone = details_data.get("formatted_phone_number", "")
                website = details_data.get("website", "")

        results.append({
            "company_name": place.get("name", ""),
            "industry": industry,
            "city": city,
            "website": website,
            "phone": phone,
            "email": "",
            "source": "Google Places",
        })

    return results