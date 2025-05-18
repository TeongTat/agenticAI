# serpapi_utils.py
import os
from serpapi import GoogleSearch

SERP_API_KEY = os.getenv("SERP_API_KEY", "your-serpapi-key")

def search_hotels(location, check_in, check_out):
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_hotels",
        "q": location,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "currency": "USD",
        "hl": "en",
        "gl": "us"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("hotels_results", [])

def format_hotel_data(hotels):
    formatted = []
    for hotel in hotels:
        name = hotel.get("name")
        price = hotel.get("price", {}).get("amount")
        rating = hotel.get("rating")
        reviews = hotel.get("reviews")
        link = hotel.get("link")

        formatted.append({
            "name": name,
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "link": link
        })
    return formatted
