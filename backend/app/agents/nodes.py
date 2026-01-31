from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
import logging

from .state import TravelState
from ..tools.flights import FlightSearchTool
from ..tools.hotels import HotelSearchTool
from ..tools.activities import ActivitySearchTool
from ..services.notifications import NotificationService

logger = logging.getLogger(__name__)


def get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


PREFERENCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly travel concierge AI helping users plan their trips.
Your job is to gather travel preferences from the user. You need to collect:
1. Destination (where they want to go)
2. Departure city (where they're traveling from)
3. Travel dates (start and end dates)
4. Budget level (budget, moderate, luxury)
5. Number of travelers
6. Interests (culture, food, adventure, relaxation, etc.)

Be conversational and helpful. Ask follow-up questions naturally.
If the user hasn't provided all information, ask for the missing details.

Current collected preferences:
{preferences}

If all required fields are collected (destination, departure_city, start_date, end_date),
end your response with [PREFERENCES_COMPLETE].

Respond naturally to the user's message."""),
    MessagesPlaceholder(variable_name="messages"),
])

ITINERARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a travel itinerary planner. Based on the user's preferences and available options,
create a personalized travel itinerary.

User preferences:
{preferences}

Available flights:
{flights}

Available hotels:
{hotels}

Available activities:
{activities}

Create a detailed day-by-day itinerary that fits their preferences and budget.
Be specific about times, locations, and recommendations.
At the end, provide a summary with total estimated cost.

End your response with [ITINERARY_READY] when you've presented the full itinerary."""),
    MessagesPlaceholder(variable_name="messages"),
])

BOOKING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a booking assistant. The user has seen their itinerary and may want to confirm their booking.

Current itinerary summary:
{itinerary_summary}

If the user wants to proceed with booking, ask for their:
1. Full name
2. Email address

Once you have both pieces of information, confirm the booking details and end with [BOOKING_CONFIRMED].

If the user wants to make changes, help them adjust the itinerary and indicate [NEEDS_CHANGES].

If the user is not ready to book, be understanding and offer to save their itinerary for later."""),
    MessagesPlaceholder(variable_name="messages"),
])


def preference_collector(state: TravelState) -> Dict[str, Any]:
    """Collect travel preferences from the user."""
    llm = get_llm()
    chain = PREFERENCE_PROMPT | llm

    preferences_str = json.dumps(state.get("preferences", {}), indent=2)

    response = chain.invoke({
        "preferences": preferences_str,
        "messages": state["messages"],
    })

    preferences = state.get("preferences", {})
    response_text = response.content

    # Parse any preferences mentioned in the conversation
    last_message = state["messages"][-1].content.lower() if state["messages"] else ""

    # Simple extraction logic
    if "paris" in last_message:
        preferences["destination"] = "Paris"
    elif "london" in last_message:
        preferences["destination"] = "London"
    elif "tokyo" in last_message:
        preferences["destination"] = "Tokyo"
    elif "rome" in last_message:
        preferences["destination"] = "Rome"
    elif "barcelona" in last_message:
        preferences["destination"] = "Barcelona"

    preferences_complete = "[PREFERENCES_COMPLETE]" in response_text
    clean_response = response_text.replace("[PREFERENCES_COMPLETE]", "").strip()

    return {
        "messages": [AIMessage(content=clean_response)],
        "preferences": preferences,
        "preferences_complete": preferences_complete,
        "current_agent": "preference_collector",
        "response": clean_response,
        "needs_user_input": True,
    }


def itinerary_planner(state: TravelState) -> Dict[str, Any]:
    """Create travel itinerary based on preferences."""
    preferences = state.get("preferences", {})

    # Search for options
    destination = preferences.get("destination", "Paris")
    departure_city = preferences.get("departure_city", "New York")
    start_date = preferences.get("start_date", "2025-06-01")
    end_date = preferences.get("end_date", "2025-06-07")

    flights_data = FlightSearchTool.search(
        departure_city=departure_city,
        arrival_city=destination,
        departure_date=start_date,
        return_date=end_date,
    )

    hotels_data = HotelSearchTool.search(
        city=destination,
        check_in=start_date,
        check_out=end_date,
    )

    activities_data = ActivitySearchTool.search(city=destination)

    # Format for LLM
    flights_str = json.dumps(flights_data, indent=2, default=str)
    hotels_str = json.dumps(hotels_data[:3], indent=2, default=str)
    activities_str = json.dumps(activities_data[:5], indent=2, default=str)

    llm = get_llm()
    chain = ITINERARY_PROMPT | llm

    response = chain.invoke({
        "preferences": json.dumps(preferences, indent=2),
        "flights": flights_str,
        "hotels": hotels_str,
        "activities": activities_str,
        "messages": state["messages"],
    })

    response_text = response.content
    clean_response = response_text.replace("[ITINERARY_READY]", "").strip()

    # Build itinerary object
    selected_flight = flights_data.get("outbound", [{}])[0] if isinstance(flights_data, dict) else {}
    return_flight = flights_data.get("return", [{}])[0] if isinstance(flights_data, dict) else {}
    selected_hotel = hotels_data[0] if hotels_data else {}

    itinerary = {
        "destination": destination,
        "departure_city": departure_city,
        "start_date": start_date,
        "end_date": end_date,
        "flights": [selected_flight, return_flight] if return_flight else [selected_flight],
        "hotels": [selected_hotel] if selected_hotel else [],
        "activities": activities_data[:3],
        "total_price": (
            selected_flight.get("price", 0) +
            (return_flight.get("price", 0) if return_flight else 0) +
            selected_hotel.get("price_per_night", 0) * 6 +
            sum(a.get("price", 0) for a in activities_data[:3])
        ),
    }

    return {
        "messages": [AIMessage(content=clean_response)],
        "itinerary": itinerary,
        "selected_flights": itinerary["flights"],
        "selected_hotels": itinerary["hotels"],
        "selected_activities": itinerary["activities"],
        "current_agent": "itinerary_planner",
        "response": clean_response,
        "needs_user_input": True,
    }


def booking_agent(state: TravelState) -> Dict[str, Any]:
    """Handle booking confirmation."""
    itinerary = state.get("itinerary", {})

    itinerary_summary = f"""
Destination: {itinerary.get('destination', 'N/A')}
Dates: {itinerary.get('start_date', 'N/A')} to {itinerary.get('end_date', 'N/A')}
Total Price: ${itinerary.get('total_price', 0):.2f}
"""

    llm = get_llm()
    chain = BOOKING_PROMPT | llm

    response = chain.invoke({
        "itinerary_summary": itinerary_summary,
        "messages": state["messages"],
    })

    response_text = response.content
    booking_confirmed = "[BOOKING_CONFIRMED]" in response_text
    clean_response = response_text.replace("[BOOKING_CONFIRMED]", "").replace("[NEEDS_CHANGES]", "").strip()

    booking_details = None
    if booking_confirmed:
        # Extract booking details from conversation
        booking_details = {
            "itinerary": itinerary,
            "status": "confirmed",
        }

    return {
        "messages": [AIMessage(content=clean_response)],
        "booking_confirmed": booking_confirmed,
        "booking_details": booking_details,
        "current_agent": "booking_agent",
        "response": clean_response,
        "needs_user_input": not booking_confirmed,
    }


def notification_agent(state: TravelState) -> Dict[str, Any]:
    """Send notification to admin about confirmed booking."""
    booking_details = state.get("booking_details", {})
    itinerary = state.get("itinerary", {})

    notification_data = {
        "id": state.get("session_id", "unknown"),
        "user_name": booking_details.get("user_name", "Guest"),
        "user_email": booking_details.get("user_email", "unknown@example.com"),
        "destination": itinerary.get("destination", "Unknown"),
        "total_price": itinerary.get("total_price", 0),
    }

    NotificationService.notify_admin(notification_data)

    confirmation_message = f"""
Your booking has been confirmed! Here's your confirmation:

📍 Destination: {itinerary.get('destination')}
📅 Dates: {itinerary.get('start_date')} to {itinerary.get('end_date')}
💰 Total: ${itinerary.get('total_price', 0):.2f}

A confirmation email will be sent to your email address.
Thank you for using Travel Concierge AI!
"""

    return {
        "messages": [AIMessage(content=confirmation_message)],
        "current_agent": "notification_agent",
        "response": confirmation_message,
        "needs_user_input": False,
    }
