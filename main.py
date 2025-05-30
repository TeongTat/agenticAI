import streamlit as st
import serpapi
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

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Introduction", "Emissions Visualization", "CO₂ Predictor", "Live CO₂ Level", "USA Electricity & Emissions", "Charging Stations"])

# Add content to Tab 1
with tab1:

params = {
  "engine": "google_flights",
  "departure_id": "PEK",
  "arrival_id": "AUS",
  "outbound_date": "2025-05-30",
  "return_date": "2025-06-05",
  "currency": "USD",
  "hl": "en",
  "api_key": "serpapi_key"
}

search = GoogleSearch(params)
results = search.get_dict()

# Inputs
destination = st.text_input("📍 Destination", placeholder="e.g., few destinations is possible with , in between...")
start_date = st.date_input("🗓️ Start Date", value=date.today())
days = st.number_input("📆 Duration (days)", min_value=1, max_value=45, value=5)
weather_info = st.text_input("☁️ Weather info", placeholder="e.g., tell me about the weather...")
flight_info = st.text_area("✈️ Flight Details (optional)", placeholder="e.g., flight arrival or other requirements...")


if st.button("🧠 Generate Itinerary"):
    if not destination:
        st.warning("Please enter a destination.")
    else:
        with st.spinner("Planning your dream adventure...."):

            # Role prompts
            system_prompt = (
                "You are the orchestrator of three expert agents: \n\n"
                "- **Travel Planner**: Creates a daily itinerary.\n"
                "- **Flight Assistant**: Provides useful insights based on given flight info and requirements.\n"
                "- **Weather Advisor**: Advises on weather at the destination.\n\n"
                "Combine their outputs into a cohesive travel plan. Be friendly, informative, and structured with markdown formatting."
            )


            user_prompt = (
                f"Plan a {days}-day trip to {destination}, starting on {start_date}. "
                f"Include key attractions, dining, and tips. "
                f"Include weather forecast for packing. "
                f"The user provided flight info: '{flight_info or 'No specific flight info'}'.\n\n"
             
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
                itinerary = response.choices[0].message.content
                st.success("Here's wonderful travel itinerary✨:")
                st.markdown(itinerary)
            except Exception as e:
                st.error(f"Error generating itinerary: {str(e)}")
