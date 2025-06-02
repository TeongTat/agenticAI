import streamlit as st
from serpapi import GoogleSearch
from openai import OpenAI
from datetime import date
from PIL import Image
import pandas as pd

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

# Header Image
with open("summertravel.jpg", "rb") as img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

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

# Create tabs
intro_tab, flight_tab, summary_tab = st.tabs(["Introduction", "Flight Details", "Summary"])

# Placeholder for generated content
if "generated" not in st.session_state:
    st.session_state.generated = False
    st.session_state.intro_text = ""
    st.session_state.flight_text = ""
    st.session_state.summary_text = ""

# Button
if st.button("🧠 Generate Full Travel Plan"):
    st.session_state.generated = True
    with st.spinner("Planning your dream adventure...."):

        # Tab 1 - Introduction
        intro_prompt = (
            f"Provide a travel overview for someone flying from {origin} to {destination}. "
            f"Include cultural insights, key attractions, safety tips, and general travel advice."
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": intro_prompt}
                ],
                temperature=0.7
            )
            st.session_state.intro_text = response.choices[0].message.content
        except Exception as e:
            st.session_state.intro_text = f"❌ Error generating intro: {str(e)}"

        # Tab 2 - Flight Details with SerpAPI (Now using Table)
        flight_output = ""
        flight_rows = []

        try:
            params = {
                "engine": "google_flights",
                "departure_id": origin,
                "arrival_id": destination,
                "outbound_date": start_date.strftime("%Y-%m-%d"),
                "return_date": end_date.strftime("%Y-%m-%d"),
                "currency": "USD",
                "hl": "en",
                "api_key": st.secrets["SERPAPI_KEY"]
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            best_flights = results.get("best_flights", [])

            if not best_flights:
                flight_output = "🚫 No best flights found. Please try different dates or check input codes."
            else:
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

        except Exception as e:
            flight_output = f"❌ Error retrieving flights: {str(e)}"

        # Save result
        if flight_rows:
            df_flights = pd.DataFrame(flight_rows)
            st.session_state.flight_text = df_flights
        else:
            st.session_state.flight_text = flight_output

        # Tab 3 - Summary
        summary_prompt = (
            f"You are an expert travel assistant summarizing the following information:\n"
            f"---\nINTRODUCTION:\n{st.session_state.intro_text}\n\n"
            f"---\nFLIGHT OPTIONS:\n{st.session_state.flight_text if isinstance(st.session_state.flight_text, str) else st.session_state.flight_text.to_markdown(index=False)}\n\n"
            f"The user also asked: {weather_info}\n\n"
            f"Please provide a warm, markdown-formatted summary itinerary with weather packing tips."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You summarize and polish user travel plans."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.7
            )
            st.session_state.summary_text = response.choices[0].message.content
        except Exception as e:
            st.session_state.summary_text = f"❌ Error generating summary: {str(e)}"

# Tab Display Logic
with intro_tab:
    if st.session_state.generated:
        st.markdown(st.session_state.intro_text)

with flight_tab:
    if st.session_state.generated:
        if isinstance(st.session_state.flight_text, pd.DataFrame):
            st.dataframe(st.session_state.flight_text, use_container_width=True)
        else:
            st.markdown(st.session_state.flight_text)

with summary_tab:
    if st.session_state.generated:
        st.markdown(st.session_state.summary_text)
