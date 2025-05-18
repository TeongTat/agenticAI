# agentic_core.py

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.agents import Tool
from pydantic import BaseModel
from typing import Optional

llm = ChatOpenAI(model_name="gpt-4", temperature=0.4)

# Define Pydantic input for analyze_hotels
class HotelInput(BaseModel):
    hotel_data: str

def analyze_hotels_fn(hotel_data: str) -> str:
    return llm([
        SystemMessage(content="You are an expert travel agent."),
        HumanMessage(content=f"""Based on the following hotel listings:\n{hotel_data}

Please recommend the best hotel considering:
- Price
- Guest Rating
- Location
- Amenities

Structure the recommendation with a summary and bullet points.""")
    ]).content

analyze_hotels = Tool.from_function(
    func=analyze_hotels_fn,
    name="analyze_hotels",
    description="Analyzes hotel data and returns the best recommendation",
    args_schema=HotelInput
)


# Create itinerary tool
class ItineraryInput(BaseModel):
    destination: str
    flight_info: str
    hotel_info: str
    days: int

def create_itinerary_fn(destination: str, flight_info: str, hotel_info: str, days: int) -> str:
    return llm([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=f"""Create a {days}-day itinerary for a trip to {destination}.

**Flight Info**:
{flight_info}

**Hotel Info**:
{hotel_info}

Include:
- Hotel check-in/out
- Day-wise activities
- Food recommendations 🍜
- Landmarks 🏞️
- Transport tips 🚇
- Emoji headers

Format in Markdown.""")
    ]).content

create_itinerary = Tool.from_function(
    func=create_itinerary_fn,
    name="create_itinerary",
    description="Generates a markdown itinerary using flight, hotel, and destination info.",
    args_schema=ItineraryInput
)
