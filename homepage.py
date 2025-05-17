import streamlit as st
from openai import OpenAI
from datetime import date
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import os

# Initialize OpenAI client using secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

with open("agentictravel.jpg", "rb") as img_file:
        image = Image.open(img_file)
        st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

# Inputs
destination = st.text_input("📍 Destination", placeholder="e.g., few destinations is possible with , in between...")
start_date = st.date_input("🗓️ Start Date", value=date.today())
days = st.number_input("📆 Duration (days)", min_value=1, max_value=45, value=5)
flight_info = st.text_area("✈️ Flight Details (optional)", placeholder="e.g., flight arrival or other requirements...")

# Simulated weather API function (you can replace this with real data)
def get_mock_weather(dest, start_date):
    return f"Expect sunny weather with mild temperatures (~22°C) in {dest} starting from {start_date.strftime('%B %d')}."

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

            weather_info = get_mock_weather(destination, start_date)

            user_prompt = (
                f"Plan a {days}-day trip to {destination}, starting on {start_date}. "
                f"Include key attractions, dining, and tips. "
                f"The user provided flight info: '{flight_info or 'No specific flight info'}'.\n\n"
                f"Weather assistant reports: {weather_info}"
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
                st.success("Here's your multi-agent itinerary:")
                st.markdown(itinerary)
            except Exception as e:
                st.error(f"Error generating itinerary: {str(e)}")
