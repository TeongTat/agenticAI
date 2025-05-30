import streamlit as st
from openai import OpenAI
from datetime import date
from PIL import Image
import pandas as pd
from serpapi import GoogleSearch
import os

# Initialize OpenAI client using secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="wide")
st.title("🌍 Awesome Travel Planner")

# Header image
with open("summertravel.jpg", "rb") as img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

# Central input fields
with st.container():
    st.subheader("✈️ Trip Details")
    departure_city = st.text_input("Departure Airport Code (e.g., KUL)")
    arrival_city = st.text_input("Arrival Airport Code (e.g., NRT)")
    departure_date = st.date_input("Departure Date", value=date.today())
    return_date = st.date_input("Return Date", value=date.today())
    currency = st.selectbox("Currency", ["USD", "MYR", "JPY", "EUR"])
    weather_info = st.text_input("☁️ Any specific weather info you want?")
    flight_info = st.text_area("Additional Flight Info", placeholder="e.g., Preferred airlines, layovers, etc.")
    generate_button = st.button("🧠 Generate Travel Plan")

# Create tabs
intro_tab, flight_tab, summary_tab = st.tabs(["📌 Introduction", "✈️ Flight Details", "🧳 Summary"])

# Process on button click
if generate_button:

    # Shared user prompt
    user_trip_info = (
        f"Trip from {departure_city} to {arrival_city}, departing {departure_date} and returning {return_date}. "
        f"Currency: {currency}. Flight info: {flight_info or 'None'}. Weather info: {weather_info or 'None'}."
    )

    # Tab 1: Introduction using OpenAI (simulating Groq)
    with intro_tab:
        st.subheader("🔍 Introduction")
        with st.spinner("Fetching travel introduction info..."):
            intro_prompt = (
                f"Give a travel overview about {arrival_city}. Include cultural tips, key attractions, and important travel advice. "
                f"The trip starts on {departure_date}."
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful travel assistant."},
                        {"role": "user", "content": intro_prompt}
                    ],
                    temperature=0.7
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error fetching introduction: {str(e)}")

    # Tab 2: Flight details using SerpAPI
    with flight_tab:
        st.subheader("✈️ Best Flight Options")
        with st.spinner("Fetching flight data from SerpAPI..."):
            params = {
                "engine": "google_flights",
                "departure_id": departure_city,
                "arrival_id": arrival_city,
                "outbound_date": departure_date.strftime("%Y-%m-%d"),
                "return_date": return_date.strftime("%Y-%m-%d"),
                "currency": currency,
                "hl": "en",
                "api_key": st.secrets["SERPAPI_KEY"]
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            best_flights = results.get("best_flights", [])

            if not best_flights:
                st.warning("No best flights found.")
            else:
                flight_data = []
                for option in best_flights:
                    total_duration = option.get("total_duration", "N/A")
                    total_emissions = option.get("carbon_emissions", {}).get("this_flight", None)
                    emissions_kg = f"{total_emissions / 1000:.1f}" if total_emissions else "N/A"
                    price = option.get("price", "N/A")

                    for leg in option.get("flights", []):
                        flight_data.append({
                            "Airline": leg.get("airline", "Unknown"),
                            "Flight #": leg.get("flight_number", "N/A"),
                            "From": leg.get("departure_airport", {}).get("name", "Unknown"),
                            "To": leg.get("arrival_airport", {}).get("name", "Unknown"),
                            "Departure Time": leg.get("departure_airport", {}).get("time", "N/A"),
                            "Arrival Time": leg.get("arrival_airport", {}).get("time", "N/A"),
                            "Duration (min)": leg.get("duration", "N/A"),
                            "Aircraft": leg.get("airplane", "N/A"),
                            "Class": leg.get("travel_class", "N/A"),
                            "Legroom": leg.get("legroom", "N/A"),
                            "Total Duration": total_duration,
                            "Emissions (kg)": emissions_kg,
                            "Price": price
                        })

                df = pd.DataFrame(flight_data)
                st.dataframe(df, use_container_width=True)

    # Tab 3: Summary using OpenAI
    with summary_tab:
        st.subheader("🧳 Trip Summary")
        with st.spinner("Generating your full summary..."):
            system_prompt = (
                "You are the orchestrator of three expert agents: Travel Planner, Flight Assistant, and Weather Advisor."
                " Present a helpful and inspiring trip summary using all info provided."
            )

            user_prompt = (
                f"Summarize the travel plan from {departure_city} to {arrival_city} from {departure_date} to {return_date}. "
                f"Flight info: {flight_info or 'None'}. Weather concerns: {weather_info or 'None'}."
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
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")
