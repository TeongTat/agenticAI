import streamlit as st
from datetime import datetime
from utils.weather import get_weather
from agents.travel_agent import generate_itinerary
from utils.export import export_to_pdf

st.set_page_config(page_title="Agentic AI Travel Planner", layout="centered")
st.title("🌍 Agentic AI Travel Planner")

# --- Input Section ---
st.sidebar.header("Plan Your Trip")
destination = st.sidebar.text_input("Destination", "Tokyo")
start_date = st.sidebar.date_input("Start Date", datetime.today())
end_date = st.sidebar.date_input("End Date")

if end_date < start_date:
    st.sidebar.error("End date must be after start date")
    st.stop()

activities = st.sidebar.text_area("Preferred Activities (comma-separated)", "museums, food, temples")

if st.sidebar.button("Generate Itinerary"):
    with st.spinner("Planning your trip with AI magic ✨"):
        itinerary = generate_itinerary(destination, start_date, end_date, activities)
        st.subheader(f"✈️ Your Trip to {destination}")
        st.write(itinerary)

        weather_info = get_weather(destination)
        st.subheader("☁️ Weather Forecast")
        st.write(weather_info)

        if st.button("Download Itinerary as PDF"):
            export_to_pdf(destination, itinerary)
            with open("itinerary.pdf", "rb") as f:
                st.download_button("Download PDF", f, file_name="itinerary.pdf")
