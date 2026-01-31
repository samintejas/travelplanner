from typing import TypedDict, Annotated, Sequence, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage
import operator


class TravelPreferences(TypedDict, total=False):
    destination: str
    departure_city: str
    start_date: str
    end_date: str
    budget: str
    travelers: int
    interests: List[str]
    accommodation_type: str
    special_requests: str


class TravelState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    session_id: str
    preferences: TravelPreferences
    preferences_complete: bool
    itinerary: Optional[Dict[str, Any]]
    selected_flights: List[Dict[str, Any]]
    selected_hotels: List[Dict[str, Any]]
    selected_activities: List[Dict[str, Any]]
    booking_confirmed: bool
    booking_details: Optional[Dict[str, Any]]
    current_agent: str
    needs_user_input: bool
    response: str
