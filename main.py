import streamlit as st
from serpapi import GoogleSearch
from openai import OpenAI
from datetime import date
from PIL import Image

# Setup
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="🌍 Your Personalized Travel Planner", layout="centered")
st.title("🌍 Awesome Travel Planner")

with open("summertravel.jpg", "rb") as img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

st.write("Plan your dream trip with me ✨")

# Tabs
intro_tab, flight_tab, summary_tab = st.tabs(["Introduction", "Flight details", "Summary"])

# Agent 1: Groq/Browser (simulated with placeholder function)
def groq_country_overview(destination):
    # Placeholder for Groq search - replace with actual API call or browser-based search
    return f"Here is a basic overview about {destination}. This info is extracted from a browser-based Groq agent (e.g., using DuckDuckGo)."

# Agent 2: SerpAPI flight search
def serpapi_flights(dep, arr, outbound, return_):
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": outbound,
        "return_date": return_,
        "currency": "USD",
        "hl": "en",
        "api_key": st.secrets["SERPAPI_KEY"]
    }
    search = GoogleSearch(params)
    return search.get_dict()

# Agent 3: GPT-4o Summary

def gpt_summary(destination, start_date, days, weather_info, flight_info, overview):
    user_prompt = f"""
    Using the following information:
    - Destination: {destination}
    - Start Date: {start_date}
    - Duration: {days} days
    - Weather: {weather_info}
    - Flight Info: {flight_info}
    - Country Overview: {overview}

    Create a detailed, friendly, markdown-formatted travel itinerary including packing tips, key attractions, and logistics.
    """

    system_prompt = "You are a smart travel assistant summarizing insights from multiple expert agents."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# User Inputs (shared)
destination = st.text_input("📍 Destination", placeholder="e.g., Japan, Korea, etc.")
start_date = st.date_input("🗓️ Start Date", value=date.today())
days = st.number_input("🗖️ Duration (days)", min_value=1, max_value=45, value=5)
weather_info = st.text_input("☁️ Weather info", placeholder="e.g., tell me about the weather...")
flight_info = st.text_area("✈️ Flight Details (optional)", placeholder="e.g., flight arrival or other requirements...")

# Tab 1: Introduction
with intro_tab:
    if destination:
        overview = groq_country_overview(destination)
        st.markdown(f"**Destination Overview:**\n\n{overview}")
    else:
        st.info("Enter a destination above to get started.")

# Tab 2: Flights
with flight_tab:
    dep = st.text_input("🎢 Departure Airport Code", key="dep")
    arr = st.text_input("🎢 Arrival Airport Code", key="arr")
    outbound = st.date_input("🌐 Departure Date", key="out")
    return_ = st.date_input("🌐 Return Date", key="ret")

    if st.button("🚀 Search Flights"):
        if dep and arr:
            flight_data = serpapi_flights(dep, arr, outbound.isoformat(), return_.isoformat())
            st.json(flight_data)
        else:
            st.warning("Please enter both departure and arrival airport codes.")

# Tab 3: Summary
with summary_tab:
    if st.button("🧐 Generate Full Itinerary"):
        if destination:
            with st.spinner("Let me put together your dream itinerary..."):
                overview = groq_country_overview(destination)
                try:
                    itinerary = gpt_summary(destination, start_date, days, weather_info, flight_info, overview)
                    st.markdown(itinerary)
                except Exception as e:
                    st.error(f"Error generating itinerary: {str(e)}")
        else:
            st.warning("Please enter a destination above.")
