# main.py
import streamlit as st
from datetime import date, timedelta
from serpapi_utils import search_hotels, format_hotel_data
from agentic_core import analyze_hotels, create_itinerary

st.set_page_config(page_title="🌍 Travel AI Planner", layout="centered")
st.title("✈️ AI Travel Planner")
with open("summertravel.jpg", "rb") as img_file:
        image = Image.open(img_file)
        st.image(image, use_container_width=True)
        
st.markdown("Plan your dream trip with hotel suggestions and a full itinerary 🌴")

# --- User Inputs ---
col1, col2 = st.columns(2)
location = col1.text_input("📍 Destination", "Tokyo")
check_in = col1.date_input("Check-in Date", date.today() + timedelta(days=7))
check_out = col2.date_input("Check-out Date", check_in + timedelta(days=3))

if st.button("🔍 Search Hotels & Generate Plan"):
    with st.spinner("Searching hotels..."):
        hotels = search_hotels(location, check_in.isoformat(), check_out.isoformat())
        hotel_text = format_hotel_data(hotels)

    st.subheader("🏨 Top Hotels")
    st.text(hotel_text)

    with st.spinner("Analyzing hotels with AI..."):
        hotel_reco = analyze_hotels.run(hotel_text)
        st.success("✅ Hotel recommendation ready")
        st.markdown(hotel_reco)

    days = (check_out - check_in).days
    fake_flight = f"Arriving in {location} on {check_in} at 9:00 AM, returning on {check_out} at 5:00 PM"

    with st.spinner("🗺️ Creating Itinerary..."):
        itinerary = create_itinerary.run(location, fake_flight, hotel_reco, days)
        st.markdown(itinerary)
