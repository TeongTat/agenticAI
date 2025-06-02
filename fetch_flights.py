import json
from serpapi import GoogleSearch
from datetime import date

def fetch_and_save_flights(origin, destination, start_date, end_date, output_file="data/flights.json"):
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": start_date.strftime("%Y-%m-%d"),
        "return_date": end_date.strftime("%Y-%m-%d"),
        "currency": "USD",
        "hl": "en",
        "api_key": "YOUR_SERPAPI_KEY"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    best_flights = results.get("best_flights", [])

    flight_rows = []

    for option in best_flights:
        total_duration = option.get("total_duration", "N/A")
        total_emissions = option.get("carbon_emissions", {}).get("this_flight")
        emissions_kg = f"{total_emissions / 1000:.1f}" if total_emissions else "N/A"
        price = option.get("price", "N/A")

        segments = []
        for leg in option.get("flights", []):
            airline = leg.get("airline", "Unknown Airline")
            flight_no = leg.get("flight_number", "N/A")
            from_airport = leg.get("departure_airport", {}).get("name", "Unknown Departure")
            to_airport = leg.get("arrival_airport", {}).get("name", "Unknown Arrival")
            depart_time = leg.get("departure_airport", {}).get("time", "N/A")
            arrive_time = leg.get("arrival_airport", {}).get("time", "N/A")
            duration = leg.get("duration", "N/A")

            segments.append(
                f"{airline} {flight_no} ({from_airport} ➡ {to_airport})\n"
                f"🕒 {depart_time} → {arrive_time} | {duration} min"
            )

        flight_rows.append({
            "Itinerary": "\n\n".join(segments),
            "Total Duration (min)": total_duration,
            "Emissions (kg CO₂)": emissions_kg,
            "Price (USD)": price
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(flight_rows, f, indent=2)
    print(f"✅ Saved {len(flight_rows)} flights to {output_file}")


# Example usage
if __name__ == "__main__":
    fetch_and_save_flights("PEK", "AUS", date.today(), date.today())
