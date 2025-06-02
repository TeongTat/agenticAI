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
        with flight_tab:
            if st.session_state.generated:
                try:
                    with open("data/flights.json", "r", encoding="utf-8") as f:
                        flight_data = json.load(f)
                        df_flights = pd.DataFrame(flight_data)
                        st.dataframe(df_flights, use_container_width=True)
                except Exception as e:
                        st.error(f"❌ Could not load flight data: {str(e)}")

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
