# serpapi_utils.py
import os
from serpapi import GoogleSearch

SERP_API_KEY = os.getenv("SERP_API_KEY", "your-serpapi-key")

def search_hotels(location: str, checkin: str, checkout: str):
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_hotels",
        "q": location,
        "check_in_date": checkin,
        "check_out_date": checkout,
        "currency": "USD",
        "sort_by": 3
    }
    result = GoogleSearch(params).get_dict()
    return result.get("properties", [])

def format_hotel_data(hotels) -> str:
    output = ""
    for hotel in hotels[:5]:
        name = hotel.get("name", "")
        price = hotel.get("price", {}).get("display", "N/A")
        rating = hotel.get("rating", "N/A")
        location = hotel.get("address", "")
        link = hotel.get("link", "")
        output += f"{name} | {price} | ⭐ {rating} | 📍 {location} | 🔗 {link}\n"
    return output
