import streamlit as st
from serpapi import GoogleSearch
from openai import OpenAI
from datetime import date
from io import BytesIO
from PIL import Image
import os

# Initialize OpenAI client using secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

with open("summertravel.jpg", "rb") as img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

# Main input section (applies across all tabs)
st.header("✏️ Trip Information")
departure = st.text_input("🛫 Departure Airport Code", placeholder="e.g., KUL")
arrival = st.text_input("🛬 Arrival Airport Code", placeholder="e.g., NRT")
destination = st.text_input("📍 Destination Description", placeholder="e.g., Tokyo, Japan")
outbound_date = st.date_input("🗓️ Departure Date", value=date.today())
return_date = st.date_input("🗓️ Return Date", value=date.today())
duration = (return_date - outbound_date).days
flight_info = st.text_area("✈️ Flight Notes (optional)", placeholder="e.g., preferred airlines, layover requirements...")
weather_info = st.text_input("☁️ Weather info", placeholder="e.g., tell me about the weather...")

# Pre-fetch Groq-style data and SerpAPI before tabs
basic_info = f"You are going to {destination}. Here's a summary of the place, culture, and must-knows. (Groq-agent would provide this)"

# Get flight details using SerpAPI
flight_results = {}
if departure and arrival:
    params = {
        "engine": "google_flights",
        "departure_id": departure,
        "arrival_id": arrival,
        "outbound_date": outbound_date.strftime("%Y-%m-%d"),
        "return_date": return_date.strftime("%Y-%m-%d"),
        "currency": "USD",
        "hl": "en",
        "api_key": st.secrets["SERPAPI_API_KEY"]
    }
    search = GoogleSearch(params)
    flight_results = search.get_dict()

# Tabs
intro_tab, flights_tab, summary_tab = st.tabs(["Introduction", "Flight Details", "Summary"])

with intro_tab:
    st.subheader("📖 Destination Overview")
    st.markdown(basic_info)

with flights_tab:
    st.subheader("✈️ Flight Options")
    best_flights = flight_results.get('best_flights', [])

    if not best_flights:
        st.info("No flight options found.")
    else:
        for i, option in enumerate(best_flights, 1):
            st.markdown(f"### ✈️ Itinerary #{i}")
            total_duration = option.get('total_duration', 'N/A')
            emissions = option.get('carbon_emissions', {}).get('this_flight', None)
            emissions_kg = f"{emissions / 1000:.1f} kg" if emissions else "N/A"
            price = option.get('price', 'N/A')

            st.write(f"**💰 Price**: ${price}")
            st.write(f"**🕒 Duration**: {total_duration} min")
            st.write(f"**🌍 Emissions**: {emissions_kg}")

            for leg in option.get('flights', []):
                with st.expander(f"{leg.get('airline', 'Unknown')} Flight {leg.get('flight_number', 'N/A')}"):
                    st.write(f"From **{leg.get('departure_airport', {}).get('name', 'Unknown')}** at {leg.get('departure_airport', {}).get('time', 'N/A')}")
                    st.write(f"To **{leg.get('arrival_airport', {}).get('name', 'Unknown')}** at {leg.get('arrival_airport', {}).get('time', 'N/A')}")
                    st.write(f"- Duration: {leg.get('duration', 'N/A')} min")
                    st.write(f"- Aircraft: {leg.get('airplane', 'N/A')}")
                    st.write(f"- Class: {leg.get('travel_class', 'N/A')} | Legroom: {leg.get('legroom', 'N/A')}")

with summary_tab:
    st.subheader("🧠 AI Trip Summary")
    if destination:
        with st.spinner("Synthesizing your trip summary..."):
            system_prompt = (
                "You are the orchestrator of three expert agents: Travel Planner, Flight Assistant, and Weather Advisor. "
                "Based on user's travel details and results, combine their outputs into a cohesive travel summary with markdown formatting."
            )

            user_prompt = (
                f"Plan a {duration}-day trip to {destination}, departing on {outbound_date}.\n"
                f"Destination background: {basic_info}.\n"
                f"Flight preferences or notes: {flight_info or 'No preferences given'}.\n"
                f"Flight summary from search: {len(best_flights)} options were returned.\n"
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
                summary = response.choices[0].message.content
                st.markdown(summary)
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")
    else:
        st.info("Please enter trip details above to generate a summary.")
