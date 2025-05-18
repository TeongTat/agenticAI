# agentic_core.py
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import tool
from pydantic import BaseModel

llm = ChatOpenAI(model_name="gpt-4", temperature=0.4)

# Define input schema for analyze_hotels
class HotelAnalysisInput(BaseModel):
    hotel_data: str

@tool(args_schema=HotelAnalysisInput)
def analyze_hotels(hotel_data: str) -> str:
    """Analyze hotel data and return the best recommendation."""
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

# Define input schema for create_itinerary
class ItineraryInput(BaseModel):
    destination: str
    flight_info: str
    hotel_info: str
    days: int

@tool(args_schema=ItineraryInput)
def create_itinerary(destination: str, flight_info: str, hotel_info: str, days: int) -> str:
    """Generate a visually appealing itinerary with headers and emojis."""
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
