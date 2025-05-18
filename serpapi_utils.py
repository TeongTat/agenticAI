from serpapi import GoogleSearch
import os

SERP_API_KEY = os.getenv("SERP_API_KEY", "your-serpapi-key")

def search_flights(departure_id, arrival_id, outbound_date, return_date=None, currency="USD"):
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": currency,
    }

    if return_date:
        params["return_date"] = return_date

    search = GoogleSearch(params)
    return search.get_dict()
