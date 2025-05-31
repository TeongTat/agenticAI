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
    origin_country = st.text_input("🛫 Departure Country", value="China")
    destination_country = st.text_input("📍 Destination Country", value="United States")
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
    st.session_state.flight_df = pd.DataFrame()
    st.session_state.summary_text = ""

# Button
if st.button("🧠 Generate Full Travel Plan"):
    st.session_state.generated = True
    with st.spinner("Planning your dream adventure...."):

        ## Tab 1 - Introduction (using GPT)
        intro_prompt = (
            f"Provide a travel overview for someone flying from {origin_country} to {destination_country}. "
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

        ## Tab 2 - Flight Details using SerpAPI
        try:
            # Use fixed airport codes for now as placeholders
            airport_mapping = {
                "China": "PEK",  # Beijing
                "United States": "AUS"  # Austin
            }
            origin = airport_mapping.get(origin_country, "PEK")
            destination = airport_mapping.get(destination_country, "AUS")

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
                st.session_state.flight_df = pd.DataFrame()
            else:
                rows = []
                for option in best_flights:
                    total_duration = option.get("total_duration", "N/A")
                    total_emissions = option.get("carbon_emissions", {}).get("this_flight")
                    emissions_kg = f"{total_emissions / 1000:.1f}" if total_emissions else "N/A"
                    price = option.get("price", "N/A")

                    for leg in option.get("flights", []):
                        row = {
                            "Airline": leg.get("airline", "Unknown"),
                            "Flight #": leg.get("flight_number", "N/A"),
                            "From": leg.get("departure_airport", {}).get("name", "Unknown"),
                            "To": leg.get("arrival_airport", {}).get("name", "Unknown"),
                            "Departure": leg.get("departure_airport", {}).get("time", "N/A"),
                            "Arrival": leg.get("arrival_airport", {}).get("time", "N/A"),
                            "Duration (min)": leg.get("duration", "N/A"),
                            "Aircraft": leg.get("airplane", "N/A"),
                            "Class": leg.get("travel_class", "N/A"),
                            "Legroom": leg.get("legroom", "N/A"),
                            "Total Price ($)": price,
                            "Total Duration": total_duration,
                            "Emissions (kg)": emissions_kg
                        }
                        rows.append(row)

                st.session_state.flight_df = pd.DataFrame(rows)

        except Exception as e:
            st.session_state.flight_df = pd.DataFrame({"Error": [str(e)]})

        ## Tab 3 - Summary
        summary_prompt = f"""
        Create a comprehensive summary travel plan for a trip from {origin_country} to {destination_country}
        departing on {start_date} and returning on {end_date}.
        Include highlights from the introduction and flight details.
        User's weather query: {weather_info}
        Make it informative, well-structured, and reader-friendly.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You summarize and polish user travel plans."},
                    {"role": "user", "content": summary_prompt + "\n\n" + st.session_state.intro_text}
                ],
                temperature=0.7
            )
            st.session_state.summary_text = response.choices[0].message.content
        except Exception as e:
            st.session_state.summary_text = f"❌ Error generating summary: {str(e)}"

# Display content per tab
with intro_tab:
    if st.session_state.generated:
        st.markdown(st.session_state.intro_text)

with flight_tab:
    if st.session_state.generated:
        if not st.session_state.flight_df.empty:
            st.dataframe(st.session_state.flight_df, use_container_width=True)
        else:
            st.warning("No flights found. Try adjusting your dates or input.")

with summary_tab:
    if st.session_state.generated:
        st.markdown(st.session_state.summary_text)
