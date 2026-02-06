"""Multi-agent orchestration for travel concierge."""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from data import search_flights, search_hotels, search_activities, get_travel_guide


class AgentType(Enum):
    COORDINATOR = "coordinator"
    FLIGHT_AGENT = "flight_agent"
    HOTEL_AGENT = "hotel_agent"
    ACTIVITY_AGENT = "activity_agent"
    GUIDE_AGENT = "guide_agent"


@dataclass
class TravelPreferences:
    destination: Optional[str] = None
    origin: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    travel_style: Optional[str] = None  # budget, moderate, luxury
    interests: list = field(default_factory=list)


@dataclass
class Booking:
    booking_type: str  # flight, hotel, activity
    item_id: str
    details: dict
    confirmed: bool = False


@dataclass
class Itinerary:
    preferences: TravelPreferences
    flights: list = field(default_factory=list)
    hotels: list = field(default_factory=list)
    activities: list = field(default_factory=list)
    total_cost: float = 0.0
    confirmed: bool = False


class FlightAgent:
    """Agent specialized in flight search and booking."""

    def search(self, origin: str = None, destination: str = None, date: str = None) -> list:
        return search_flights(origin, destination, date)

    def format_results(self, flights: list) -> str:
        if not flights:
            return "No flights found matching your criteria."

        result = "**Available Flights:**\n\n"
        for f in flights:
            result += f"- **{f['airline']}** ({f['id']})\n"
            result += f"  {f['from']} → {f['to']}\n"
            result += f"  Departure: {f['departure']} | Arrival: {f['arrival']}\n"
            result += f"  Price: ${f['price']} ({f['class']})\n\n"
        return result


class HotelAgent:
    """Agent specialized in hotel search and booking."""

    def search(self, city: str = None, max_price: float = None) -> list:
        return search_hotels(city, max_price)

    def format_results(self, hotels: list) -> str:
        if not hotels:
            return "No hotels found matching your criteria."

        result = "**Available Hotels:**\n\n"
        for h in hotels:
            result += f"- **{h['name']}** ({h['id']}) - {h['city']}\n"
            result += f"  Rating: {'⭐' * int(h['rating'])} ({h['rating']})\n"
            result += f"  Price: ${h['price_per_night']}/night\n"
            result += f"  Amenities: {', '.join(h['amenities'])}\n"
            result += f"  {h['description']}\n\n"
        return result


class ActivityAgent:
    """Agent specialized in activity search and booking."""

    def search(self, city: str = None) -> list:
        return search_activities(city)

    def format_results(self, activities: list) -> str:
        if not activities:
            return "No activities found for this destination."

        result = "**Available Activities:**\n\n"
        for a in activities:
            result += f"- **{a['name']}** ({a['id']})\n"
            result += f"  Location: {a['city']} | Duration: {a['duration']}\n"
            result += f"  Price: ${a['price']}\n"
            result += f"  {a['description']}\n\n"
        return result


class GuideAgent:
    """Agent for travel guides and recommendations."""

    def get_guide(self, city: str) -> dict:
        return get_travel_guide(city)

    def format_guide(self, guide: dict) -> str:
        if not guide:
            return "Sorry, I don't have a guide for that destination yet."

        result = f"**Travel Guide: {guide['city']}**\n\n"
        result += f"**Best Time to Visit:** {guide['best_time']}\n"
        result += f"**Currency:** {guide['currency']}\n"
        result += f"**Language:** {guide['language']}\n\n"
        result += "**Must-See Attractions:**\n"
        for place in guide['must_see']:
            result += f"- {place}\n"
        result += "\n**Travel Tips:**\n"
        for tip in guide['tips']:
            result += f"- {tip}\n"
        return result


class CoordinatorAgent:
    """Main coordinator that orchestrates other agents."""

    def __init__(self):
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.activity_agent = ActivityAgent()
        self.guide_agent = GuideAgent()

    def process_intent(self, message: str, preferences: TravelPreferences) -> tuple[str, str]:
        """
        Process user message and determine intent.
        Returns (response, intent_type)
        """
        message_lower = message.lower()

        # Check for booking confirmation
        if any(word in message_lower for word in ['confirm', 'book it', 'yes book', 'proceed']):
            return "confirmation", "confirm"

        # Check for flight-related queries
        if any(word in message_lower for word in ['flight', 'fly', 'airplane', 'plane']):
            return self._handle_flight_query(message, preferences)

        # Check for hotel-related queries
        if any(word in message_lower for word in ['hotel', 'stay', 'accommodation', 'room']):
            return self._handle_hotel_query(message, preferences)

        # Check for activity-related queries
        if any(word in message_lower for word in ['activity', 'activities', 'things to do', 'tour', 'attraction']):
            return self._handle_activity_query(message, preferences)

        # Check for travel guide queries
        if any(word in message_lower for word in ['guide', 'tips', 'advice', 'recommend', 'must see', 'best time']):
            return self._handle_guide_query(message, preferences)

        # Check for destination mentions and update preferences
        destinations = ['paris', 'london', 'tokyo', 'rome', 'new york', 'los angeles']
        for dest in destinations:
            if dest in message_lower:
                preferences.destination = dest.title()
                break

        # Default: try to understand travel planning intent
        return self._handle_general_query(message, preferences)

    def _handle_flight_query(self, message: str, prefs: TravelPreferences) -> tuple[str, str]:
        flights = self.flight_agent.search(
            origin=prefs.origin,
            destination=prefs.destination,
            date=prefs.start_date
        )
        return self.flight_agent.format_results(flights[:5]), "flight_search"

    def _handle_hotel_query(self, message: str, prefs: TravelPreferences) -> tuple[str, str]:
        max_price = None
        if prefs.travel_style == 'budget':
            max_price = 150
        elif prefs.travel_style == 'moderate':
            max_price = 250

        hotels = self.hotel_agent.search(city=prefs.destination, max_price=max_price)
        return self.hotel_agent.format_results(hotels[:5]), "hotel_search"

    def _handle_activity_query(self, message: str, prefs: TravelPreferences) -> tuple[str, str]:
        activities = self.activity_agent.search(city=prefs.destination)
        return self.activity_agent.format_results(activities), "activity_search"

    def _handle_guide_query(self, message: str, prefs: TravelPreferences) -> tuple[str, str]:
        if prefs.destination:
            guide = self.guide_agent.get_guide(prefs.destination)
            return self.guide_agent.format_guide(guide), "guide"
        return "Which destination would you like travel tips for?", "guide_request"

    def _handle_general_query(self, message: str, prefs: TravelPreferences) -> tuple[str, str]:
        if not prefs.destination:
            return (
                "Welcome to Travel Concierge! I'd love to help you plan your perfect trip.\n\n"
                "To get started, tell me:\n"
                "- Where would you like to go?\n"
                "- When are you planning to travel?\n"
                "- What's your approximate budget?\n"
                "- What kind of experience are you looking for? (adventure, relaxation, culture, etc.)\n\n"
                "Available destinations I have info for: Paris, London, Tokyo, Rome"
            ), "greeting"

        # We have a destination, offer options
        return (
            f"Great choice! I can help you plan your trip to **{prefs.destination}**.\n\n"
            "What would you like to explore?\n"
            "- Search for **flights**\n"
            "- Find **hotels**\n"
            "- Discover **activities** and tours\n"
            "- Get **travel tips** and guides\n\n"
            "Just let me know what interests you!"
        ), "options"

    def generate_itinerary_summary(self, itinerary: Itinerary) -> str:
        """Generate a summary of the current itinerary."""
        if not itinerary.flights and not itinerary.hotels and not itinerary.activities:
            return "Your itinerary is empty. Start by searching for flights, hotels, or activities!"

        summary = "**Your Travel Itinerary**\n\n"

        if itinerary.preferences.destination:
            summary += f"**Destination:** {itinerary.preferences.destination}\n\n"

        if itinerary.flights:
            summary += "**Flights:**\n"
            for f in itinerary.flights:
                summary += f"- {f['airline']}: {f['from']} → {f['to']} (${f['price']})\n"
            summary += "\n"

        if itinerary.hotels:
            summary += "**Hotels:**\n"
            for h in itinerary.hotels:
                summary += f"- {h['name']} - ${h['price_per_night']}/night\n"
            summary += "\n"

        if itinerary.activities:
            summary += "**Activities:**\n"
            for a in itinerary.activities:
                summary += f"- {a['name']} (${a['price']})\n"
            summary += "\n"

        summary += f"**Estimated Total:** ${itinerary.total_cost:.2f}\n\n"

        if not itinerary.confirmed:
            summary += "Type **'confirm booking'** to finalize your itinerary!"
        else:
            summary += "✅ **Booking Confirmed!**"

        return summary
