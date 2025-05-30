import streamlit as st
from serpapi import GoogleSearch
from openai import OpenAI
from datetime import date
from PIL import Image
import pandas as pd

# Page config
st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

# Banner image
with open("summertravel.jpg", "rb") as img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

# User inputs
with st.form("travel_form"):
    departure = st.text_input("🛫 Departure Airport Code", max_chars=3)
    arrival = st.text_input("🛬 Arrival Airport Code", max_chars=3)
    start_date = st.date_input("🗓️ Departure Date", value=date.today())
    return_date = st.date_input("🗓️ Return Date")
    weather_info = st.text_input("☁️ Weather info", placeholder="e.g., Weather preferences")
    flight_info = st.text_area("✈️ Flight Details (optional)", placeholder="e.g., direct flight, no layovers...")
    submit = st.form_submit_button("🧠 Generate Full Travel Plan")

# Tabs
intro_tab, flight_tab, summary_tab = st.tabs(["Introduction", "Flight Details", "Summary"])

if submit:
    # OpenAI setup
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # -- TAB 1: Introduction Content --
    with intro_tab:
        with st.spinner("🌍 Fetching destination overview..."):
            intro_prompt = f"Provide an engaging travel overview for {arrival}. Include cultural highlights, popular attractions, travel tips, and anything a traveler should know."

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful travel assistant."},
                        {"role": "user", "content": intro_prompt}
                    ]
                )
                intro_summary = response.choices[0].message.content
                st.markdown(intro_summary)
            except Exception as e:
                st.error(f"❌ Error fetching introduction: {str(e)}")

    # -- TAB 2: Flight Details --
    with flight_tab:
        with st.spinner("✈️ Searching flight options..."):
            params = {
                "engine": "google_flights",
                "departure_id": departure,
                "arrival_id": arrival,
                "outbound_date": start_date.strftime('%Y-%m-%d'),
                "return_date": return_date.strftime('%Y-%m-%d'),
                "currency": "USD",
                "hl": "en",
                "api_key": st.secrets["SERPAPI_KEY"]
            }

            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                best_flights = results.get('best_flights', [])

                if not best_flights:
                    st.warning("No best flights found.")
                else:
                    flight_rows = []
                    for option in best_flights:
                        price = option.get('price', 'N/A')
                        total_duration = option.get('total_duration', 'N/A')
                        emissions = option.get('carbon_emissions', {}).get('this_flight', None)
                        emissions_kg = f"{emissions / 1000:.1f} kg" if emissions else "N/A"

                        for leg in option.get('flights', []):
                            flight_rows.append({
                                "Airline": leg.get('airline', 'Unknown'),
                                "Flight #": leg.get('flight_number', 'N/A'),
                                "From": leg.get('departure_airport', {}).get('name', 'Unknown'),
                                "To": leg.get('arrival_airport', {}).get('name', 'Unknown'),
                                "Depart": leg.get('departure_airport', {}).get('time', 'N/A'),
                                "Arrive": leg.get('arrival_airport', {}).get('time', 'N/A'),
                                "Duration": leg.get('duration', 'N/A'),
                                "Class": leg.get('travel_class', 'N/A'),
                                "Aircraft": leg.get('airplane', 'N/A'),
                                "Legroom": leg.get('legroom', 'N/A'),
                                "Price": price,
                                "Trip Duration": total_duration,
                                "Emissions": emissions_kg
                            })

                    df_flights = pd.DataFrame(flight_rows)
                    st.dataframe(df_flights, use_container_width=True)

            except Exception as e:
                st.error(f"❌ Error fetching flights: {str(e)}")

    # -- TAB 3: Summary --
    with summary_tab:
        with st.spinner("🧳 Compiling summary plan..."):
            summary_prompt = (
                f"You are a travel assistant. Summarize a complete travel plan for a round trip from {departure} to {arrival},"
                f" departing on {start_date} and returning on {return_date}. Include key destination info, flight suggestions, weather and packing tips, and any useful advice based on user's input: {flight_info}, {weather_info}."
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert travel assistant generating full trip itineraries."},
                        {"role": "user", "content": summary_prompt}
                    ]
                )
                itinerary = response.choices[0].message.content
                st.markdown(itinerary)
            except Exception as e:
                st.error(f"❌ Error creating summary: {str(e)}")
