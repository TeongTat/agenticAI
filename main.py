import streamlit as st
import serpapi
from serpapi import GoogleSearch
from openai import OpenAI
from datetime import date
from PIL import Image

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

with open("summertravel.jpg", "rb") as img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

# Input section
st.header("📌 Trip Details")
departure = st.text_input("Departing Country / City", placeholder="e.g., Tokyo")
arrival = st.text_input("Arrival Country / City", placeholder="e.g., Paris")
start_date = st.date_input("🗓️ Departure Date", value=date.today())
return_date = st.date_input("🗓️ Return Date", value=date.today())
days = st.number_input("📆 Duration (days)", min_value=1, max_value=45, value=5)
weather_info = st.text_input("☁️ Weather info", placeholder="e.g., general query about weather...")
flight_info = st.text_area("✈️ Flight Details (optional)", placeholder="e.g., preferred airline, cabin class, etc.")

run_query = st.button("🧠 Generate Full Travel Plan")

# Define placeholders for output
generated_tab1, generated_tab2, generated_tab3 = None, None, None

if run_query and departure and arrival:
    st.success("Generating full travel plan based on your inputs!")

    # --- Tab 1: Groq/Browser-based Overview (Simulated) ---
    generated_tab1 = f"""
### 🌏 Destination Overview: {arrival}
- Capital: Example City
- Currency: Example Dollar (EXD)
- Language: Exampleese
- Visa Requirement: Required for over 30 days stay

Useful travel tips:
- Carry cash, not all places accept cards
- Public transport is widely available
"""

    # --- Tab 2: Flights with SerpAPI ---
    flight_results = ""
    try:
        params = {
            "engine": "google_flights",
            "departure_id": departure[:3].upper(),
            "arrival_id": arrival[:3].upper(),
            "outbound_date": str(start_date),
            "return_date": str(return_date),
            "currency": "USD",
            "hl": "en",
            "api_key": st.secrets["SERPAPI_KEY"]
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        best_flights = results.get('best_flights', [])

        if not best_flights:
            flight_results = "No best flights found."
        else:
            for i, option in enumerate(best_flights, 1):
                flight_results += f"\n✈️ **Itinerary #{i}**\n"
                flight_results += "-" * 50 + "\n"
                total_duration = option.get('total_duration', 'N/A')
                total_emissions = option.get('carbon_emissions', {}).get('this_flight', None)
                emissions_kg = f"{total_emissions / 1000:.1f} kg" if total_emissions else "N/A"
                price = option.get('price', 'N/A')

                for leg in option.get('flights', []):
                    airline = leg.get('airline', 'Unknown Airline')
                    flight_no = leg.get('flight_number', 'N/A')
                    from_airport = leg.get('departure_airport', {}).get('name', 'Unknown Departure')
                    to_airport = leg.get('arrival_airport', {}).get('name', 'Unknown Arrival')
                    depart_time = leg.get('departure_airport', {}).get('time', 'N/A')
                    arrive_time = leg.get('arrival_airport', {}).get('time', 'N/A')
                    duration = leg.get('duration', 'N/A')
                    aircraft = leg.get('airplane', 'N/A')
                    travel_class = leg.get('travel_class', 'N/A')
                    legroom = leg.get('legroom', 'N/A')

                    flight_results += (
                        f"- {airline} Flight {flight_no} from {from_airport} to {to_airport}\n"
                        f"  Departure: {depart_time} | Arrival: {arrive_time}\n"
                        f"  Duration: {duration} min | Aircraft: {aircraft} | Class: {travel_class} | Legroom: {legroom}\n"
                    )

                flight_results += f"💰 **Total Price**: ${price}\n"
                flight_results += f"🕒 **Total Duration**: {total_duration} min\n"
                flight_results += f"🌍 **Estimated Emissions**: {emissions_kg}\n\n"

    except Exception as e:
        flight_results = f"Error fetching flight data: {str(e)}"

    generated_tab2 = flight_results

    # --- Tab 3: Summary AI Orchestration ---
    system_prompt = (
        "You are the orchestrator of three expert agents: \n\n"
        "- Travel Planner: Creates a daily itinerary.\n"
        "- Flight Assistant: Provides useful insights based on given flight info and requirements.\n"
        "- Weather Advisor: Advises on weather at the destination.\n\n"
        "Combine their outputs into a cohesive travel plan. Be friendly, informative, and structured with markdown formatting."
    )
    user_prompt = (
        f"Plan a {days}-day trip to {arrival}, starting on {start_date}. "
        f"Include key attractions, dining, and tips. Weather query: '{weather_info or 'No weather info'}'.\n"
        f"Flight details: '{flight_info or 'No specific flight info'}'."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        generated_tab3 = response.choices[0].message.content
    except Exception as e:
        generated_tab3 = f"Error generating itinerary: {str(e)}"

# Tabs to display generated content
tab1, tab2, tab3 = st.tabs(["🌍 Introduction", "✈️ Flight Details", "🧳 Trip Summary"])

with tab1:
    st.subheader("🌍 Country Overview")
    st.markdown(generated_tab1 if generated_tab1 else "Please enter trip details and click 'Generate'.")

with tab2:
    st.subheader("✈️ Flight Search Results")
    st.markdown(generated_tab2 if generated_tab2 else "Please enter trip details and click 'Generate'.")

with tab3:
    st.subheader("🧳 Suggested Itinerary")
    st.markdown(generated_tab3 if generated_tab3 else "Please enter trip details and click 'Generate'.")
