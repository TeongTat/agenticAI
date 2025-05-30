import streamlit as st
from serpapi import GoogleSearch
from openai import OpenAI
from datetime import date
from PIL import Image
import time

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

# Image Header
with open("summertravel.jpg", "rb") as img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

# Mainframe Input Section
st.subheader("Enter your travel details below")
departure_country = st.text_input("🛫 Departure Country", placeholder="e.g., Malaysia")
arrival_country = st.text_input("🛬 Arrival Country", placeholder="e.g., Japan")
start_date = st.date_input("📅 Departure Date", value=date.today())
end_date = st.date_input("📅 Return Date", value=date.today())
weather_info = st.text_input("☁️ Weather info", placeholder="e.g., tell me about the weather...")
flight_info = st.text_area("✈️ Flight Details (optional)", placeholder="e.g., flight arrival or other requirements...")

# Tabs for outputs
tab1, tab2, tab3 = st.tabs(["Introduction", "Flight Details", "Summary"])

# Define output containers
with tab1:
    intro_container = st.empty()
with tab2:
    flight_container = st.empty()
with tab3:
    summary_container = st.empty()

# Process logic
if st.button("🧠 Generate Full Travel Plan"):
    if not departure_country or not arrival_country:
        st.warning("Please enter both departure and arrival countries.")
    else:
        with st.spinner("Planning your travel experience..."):
            # ----- Introduction Tab -----
            intro_prompt = (
                f"You are a travel guide bot. Provide a friendly, detailed introduction to {arrival_country} for someone traveling from {departure_country}. "
                f"Mention cultural highlights, top things to know, travel etiquette, and seasonal considerations for the period from {start_date} to {end_date}."
            )
            try:
                intro_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful travel information assistant."},
                        {"role": "user", "content": intro_prompt}
                    ]
                )
                intro_container.markdown(intro_response.choices[0].message.content)
            except Exception as e:
                intro_container.error(f"Introduction error: {str(e)}")

            # ----- Flight Details Tab -----
            try:
                params = {
                    "engine": "google_flights",
                    "departure_id": departure_country[:3].upper(),
                    "arrival_id": arrival_country[:3].upper(),
                    "outbound_date": start_date.strftime('%Y-%m-%d'),
                    "return_date": end_date.strftime('%Y-%m-%d'),
                    "currency": "USD",
                    "hl": "en",
                    "api_key": st.secrets["SERPAPI_KEY"]
                }
                search = GoogleSearch(params)
                results = search.get_dict()
                best_flights = results.get('best_flights', [])

                if not best_flights:
                    flight_container.warning("No best flights found.")
                else:
                    for i, option in enumerate(best_flights, 1):
                        st.markdown(f"### ✈️ Itinerary #{i}")
                        st.markdown("---")

                        total_duration = option.get('total_duration', 'N/A')
                        total_emissions = option.get('carbon_emissions', {}).get('this_flight', None)
                        emissions_kg = f"{total_emissions / 1000:.1f} kg" if total_emissions else "N/A"
                        price = option.get('price', 'N/A')

                        flight_text = ""
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

                            flight_text += (
                                f"- **{airline} Flight {flight_no}**\n"
                                f"  - From: {from_airport} → {to_airport}\n"
                                f"  - Departure: {depart_time} | Arrival: {arrive_time}\n"
                                f"  - Duration: {duration} | Aircraft: {aircraft} | Class: {travel_class} | Legroom: {legroom}\n\n"
                            )

                        flight_text += (
                            f"💰 **Total Price**: ${price}\n"
                            f"🕒 **Total Duration**: {total_duration}\n"
                            f"🌍 **Estimated Emissions**: {emissions_kg}"
                        )
                        flight_container.markdown(flight_text)
            except Exception as e:
                flight_container.error(f"Flight fetch error: {str(e)}")

            # ----- Summary Tab -----
            summary_prompt = (
                f"Summarize a complete travel plan from {departure_country} to {arrival_country} from {start_date} to {end_date}.\n"
                f"Include must-see attractions, travel tips, cultural highlights, weather advice, and flight logistics.\n"
                f"Flight info: {flight_info or 'No specific flight info provided'}.\n"
                f"Weather info: {weather_info or 'No weather context given'}."
            )
            try:
                summary_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert travel planner assistant."},
                        {"role": "user", "content": summary_prompt}
                    ]
                )
                summary_container.markdown(summary_response.choices[0].message.content)
            except Exception as e:
                summary_container.error(f"Summary error: {str(e)}")
