import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="Agentic AI Travel Planner", layout="centered")
st.title("🌍 Agentic AI Travel Planner (Open Source)")

st.markdown("""
This app uses an open-source LLM to help you plan your travels. It uses [Ollama](https://ollama.com) running locally (e.g., with `mistral`, `llama3`, etc).

Ensure you have Ollama running locally (`ollama run mistral`) before using this app.
""")

# --- User Inputs ---
destination = st.text_input("Where do you want to go?", placeholder="e.g., Tokyo, Japan")
start_date = st.date_input("Start Date", min_value=date.today())
end_date = st.date_input("End Date", min_value=start_date)
interests = st.text_area("What are your interests?", placeholder="e.g., food, culture, anime, museums, nature")

submit = st.button("✈️ Generate Itinerary")

# --- Call Ollama LLM ---
def ask_llm(prompt, model="mistral"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Agent Prompt Construction ---
def build_prompt(destination, start_date, end_date, interests):
    return f"""
You are a smart travel agent that helps create personalized travel itineraries.
Plan a day-by-day itinerary for a trip to {destination} from {start_date} to {end_date}.
Focus on the following interests: {interests}.
Include travel tips, food recommendations, and cultural etiquette where relevant.
"""

# --- Main Execution ---
if submit and destination:
    with st.spinner("Thinking like an agent... 🧠"):
        prompt = build_prompt(destination, start_date, end_date, interests)
        response = ask_llm(prompt)
    st.subheader("🗓️ Suggested Itinerary")
    st.markdown(response)
elif submit:
    st.warning("Please enter a destination before generating.")

st.markdown("---")
st.caption("Built with 💙 by Agentic AI using open-source models")
