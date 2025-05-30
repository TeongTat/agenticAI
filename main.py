import streamlit as st
from openai import OpenAI
from datetime import date
from PIL import Image
import pandas as pd
from serpapi import GoogleSearch

# Page configuration
st.set_page_config(page_title="🌍 AI Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

# Load header image
with open("summertravel.jpg", "rb") as img_file:
    st.image(Image.open(img_file), use_container_width=True)

st.write("Plan your dream trip with AI ✨")

# Mainframe Inputs
col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("🛫 Departure Airport Code", value="PEK")
    destination = st.text_input("📍 Destination Airport Code", value="AUS")
with col2:
    start_date = st.date_input("🗓️ Departure Date", value=date.today())
    end_date = st.date_input("🗓️ Return Date")

weather_info = st.text_input("☁️ Weather Questions", placeholder="e.g., What to pack for weather?")
flight_info = st.text_area("✈️ Additional Flight Preferences", placeholder="e.g., morning flight, prefer direct, etc.")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Generate Itinerary Button
if st.button("🧠 Generate Travel Plan"):
    with st.spinner("Planning your perfect adventure..."):

        # --- Introduction ---
        intro_prompt = (
            f"Give a fun, friendly overview of traveling from {origin} to {destination}. "
            f"Include travel insights, culture, what to expect and helpful tips."
        )
        intro_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful travel introduction assistant."},
                {"role": "user", "content": intro_prompt}
            ]
        )
        intro_text = intro_response.choices[0].message.content

        # --- Flight Details ---
        search_params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": str(start_date),
            "return_date": str(end_date),
            "currency": "USD",
            "hl": "en",
            "api_key": st.secrets["SERPAPI_KEY"]
        }
        flight_results = GoogleSearch(search_params).get_dict()
        best_flights = flight_results.get("best_flights", [])

        flight_table_data = []
        for option in best_flights:
            total_duration = option.get('total_duration', 'N/A')
            total_emissions = option.get('carbon_emissions', {}).get('this_flight', None)
            emissions_kg = f"{total_emissions / 1000:.1f} kg" if total_emissions else "N/A"
            price = option.get('price', 'N/A')

            for leg in option.get('flights', []):
                flight_table_data.append({
                    "Airline": leg.get('airline', 'Unknown'),
                    "Flight No.": leg.get('flight_number', 'N/A'),
                    "From": leg.get('departure_airport', {}).get('name', 'N/A'),
                    "To": leg.get('arrival_airport', {}).get('name', 'N/A'),
                    "Depart Time": leg.get('departure_airport', {}).get('time', 'N/A'),
                    "Arrive Time": leg.get('arrival_airport', {}).get('time', 'N/A'),
                    "Duration": leg.get('duration', 'N/A'),
                    "Aircraft": leg.get('airplane', 'N/A'),
                    "Class": leg.get('travel_class', 'N/A'),
                    "Legroom": leg.get('legroom', 'N/A'),
                    "Total Duration": total_duration,
                    "Emissions (kg)": emissions_kg,
                    "Price (USD)": price
                })

        flight_df = pd.DataFrame(flight_table_data)

        # --- Summary ---
        summary_prompt = (
            summary_prompt = f"""Create a comprehensive summary travel plan for a trip from {origin} to {destination}
                                 departing on {start_date} and returning on {end_date}.
                                 Include highlights from the introduction and flight details.
                                 Make it informative, well-structured, and reader-friendly."""
        )

        summary_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful travel summarizer AI."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        summary_text = summary_response.choices[0].message.content

        # Display Tabs
        tab1, tab2, tab3 = st.tabs(["Introduction", "Flight Details", "Summary"])

        with tab1:
            st.markdown(intro_text)

        with tab2:
            if flight_df.empty:
                st.warning("No flight details available.")
            else:
                st.dataframe(flight_df)

        with tab3:
            st.markdown(summary_text)
