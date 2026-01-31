from datetime import datetime
from typing import List, Optional
import random
import uuid
from langchain.tools import tool
from pydantic import BaseModel, Field


HOTEL_CHAINS = [
    {"name": "Grand Hyatt", "base_price": 250, "rating": 4.5},
    {"name": "Marriott", "base_price": 200, "rating": 4.3},
    {"name": "Hilton", "base_price": 220, "rating": 4.4},
    {"name": "Four Seasons", "base_price": 450, "rating": 4.8},
    {"name": "Holiday Inn", "base_price": 120, "rating": 3.8},
    {"name": "Best Western", "base_price": 100, "rating": 3.5},
    {"name": "Ritz-Carlton", "base_price": 500, "rating": 4.9},
    {"name": "InterContinental", "base_price": 280, "rating": 4.6},
]

AMENITIES_POOL = [
    "Free WiFi", "Pool", "Spa", "Gym", "Restaurant", "Room Service",
    "Business Center", "Concierge", "Parking", "Airport Shuttle",
    "Breakfast Included", "Pet Friendly", "Ocean View", "City View",
]

CITY_MULTIPLIERS = {
    "Paris": 1.3,
    "London": 1.4,
    "Tokyo": 1.2,
    "New York": 1.5,
    "Los Angeles": 1.1,
    "Miami": 1.0,
    "Rome": 1.1,
    "Barcelona": 1.0,
    "Sydney": 1.2,
    "Dubai": 1.4,
}


class HotelSearchInput(BaseModel):
    city: str = Field(description="City to search for hotels")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format")
    guests: int = Field(default=2, description="Number of guests")


def generate_mock_hotels(
    city: str,
    check_in: str,
    check_out: str,
    num_options: int = 4,
) -> List[dict]:
    multiplier = CITY_MULTIPLIERS.get(city, 1.0)
    hotels = []

    selected_chains = random.sample(HOTEL_CHAINS, min(num_options, len(HOTEL_CHAINS)))

    for chain in selected_chains:
        price_variation = random.uniform(0.9, 1.2)
        num_amenities = random.randint(4, 8)

        hotel = {
            "id": str(uuid.uuid4()),
            "name": f"{chain['name']} {city}",
            "city": city,
            "rating": round(chain["rating"] + random.uniform(-0.2, 0.2), 1),
            "price_per_night": round(chain["base_price"] * multiplier * price_variation, 2),
            "amenities": random.sample(AMENITIES_POOL, num_amenities),
            "check_in": check_in,
            "check_out": check_out,
        }
        hotels.append(hotel)

    return sorted(hotels, key=lambda x: x["price_per_night"])


@tool("search_hotels", args_schema=HotelSearchInput)
def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
) -> str:
    """Search for available hotels in a city for specific dates."""
    hotels = generate_mock_hotels(city, check_in, check_out)

    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
    num_nights = (check_out_date - check_in_date).days

    result = f"Found {len(hotels)} hotels in {city} for {num_nights} nights ({check_in} to {check_out}):\n\n"

    for i, hotel in enumerate(hotels, 1):
        total_price = hotel["price_per_night"] * num_nights
        result += f"{i}. {hotel['name']} ({hotel['rating']}⭐)\n"
        result += f"   ${hotel['price_per_night']}/night (Total: ${round(total_price, 2)})\n"
        result += f"   Amenities: {', '.join(hotel['amenities'][:5])}\n\n"

    return result


class HotelSearchTool:
    @staticmethod
    def search(
        city: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
    ) -> List[dict]:
        return generate_mock_hotels(city, check_in, check_out)
