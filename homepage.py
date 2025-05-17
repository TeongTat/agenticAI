# app.py
import streamlit as st
import openai
import os

# Get the API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Agentic Travel Planner", layout="centered")

st.title("🌍 Agentic AI Travel Planner")
st.write("Plan your dream trip with GPT-4o-mini ✨")

destination = st.text_input("Where do you want to go?")
days = st.number_input("How many days?", min_value=1, max_value=30, value=5)

if st.button("Generate Itinerary"):
    if not destination:
        st.warning("Please enter a destination.")
    else:
        with st.spinner("Planning your adventure..."):
            prompt = f"Act as a travel planner. Create a {days}-day travel itinerary for a trip to {destination}. Include places to visit, food recommendations, and tips."

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful and detailed travel planner."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                itinerary = response['choices'][0]['message']['content']
                st.success("Here's your itinerary:")
                st.markdown(itinerary)
            except Exception as e:
                st.error(f"Error generating itinerary: {str(e)}")
