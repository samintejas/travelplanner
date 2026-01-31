from typing import List, Optional
import random
import uuid
from langchain.tools import tool
from pydantic import BaseModel, Field


ACTIVITIES_BY_CITY = {
    "Paris": [
        {"name": "Eiffel Tower Visit", "category": "Landmark", "base_price": 30, "duration": 2},
        {"name": "Louvre Museum Tour", "category": "Museum", "base_price": 45, "duration": 4},
        {"name": "Seine River Cruise", "category": "Tour", "base_price": 25, "duration": 1.5},
        {"name": "Montmartre Walking Tour", "category": "Tour", "base_price": 35, "duration": 3},
        {"name": "French Cooking Class", "category": "Experience", "base_price": 120, "duration": 3},
        {"name": "Palace of Versailles Day Trip", "category": "Day Trip", "base_price": 80, "duration": 8},
    ],
    "London": [
        {"name": "Tower of London Tour", "category": "Landmark", "base_price": 35, "duration": 3},
        {"name": "British Museum Visit", "category": "Museum", "base_price": 0, "duration": 4},
        {"name": "Thames River Cruise", "category": "Tour", "base_price": 20, "duration": 1},
        {"name": "Harry Potter Studio Tour", "category": "Experience", "base_price": 95, "duration": 5},
        {"name": "Stonehenge Day Trip", "category": "Day Trip", "base_price": 90, "duration": 10},
        {"name": "West End Show", "category": "Entertainment", "base_price": 75, "duration": 3},
    ],
    "Tokyo": [
        {"name": "Senso-ji Temple Visit", "category": "Landmark", "base_price": 0, "duration": 2},
        {"name": "TeamLab Borderless", "category": "Museum", "base_price": 30, "duration": 3},
        {"name": "Tsukiji Fish Market Tour", "category": "Food", "base_price": 50, "duration": 3},
        {"name": "Sushi Making Class", "category": "Experience", "base_price": 85, "duration": 2},
        {"name": "Mt. Fuji Day Trip", "category": "Day Trip", "base_price": 100, "duration": 10},
        {"name": "Robot Restaurant Show", "category": "Entertainment", "base_price": 80, "duration": 2},
    ],
    "Rome": [
        {"name": "Colosseum Tour", "category": "Landmark", "base_price": 40, "duration": 3},
        {"name": "Vatican Museums", "category": "Museum", "base_price": 35, "duration": 4},
        {"name": "Pasta Making Class", "category": "Experience", "base_price": 70, "duration": 3},
        {"name": "Pompeii Day Trip", "category": "Day Trip", "base_price": 120, "duration": 10},
        {"name": "Roman Food Tour", "category": "Food", "base_price": 65, "duration": 4},
    ],
    "Barcelona": [
        {"name": "Sagrada Familia Tour", "category": "Landmark", "base_price": 35, "duration": 2},
        {"name": "Park Güell Visit", "category": "Landmark", "base_price": 15, "duration": 2},
        {"name": "Flamenco Show", "category": "Entertainment", "base_price": 45, "duration": 2},
        {"name": "Tapas Walking Tour", "category": "Food", "base_price": 75, "duration": 4},
        {"name": "Montserrat Day Trip", "category": "Day Trip", "base_price": 60, "duration": 6},
    ],
}

DEFAULT_ACTIVITIES = [
    {"name": "City Walking Tour", "category": "Tour", "base_price": 30, "duration": 3},
    {"name": "Local Food Tour", "category": "Food", "base_price": 60, "duration": 4},
    {"name": "Museum Visit", "category": "Museum", "base_price": 25, "duration": 3},
    {"name": "Cooking Class", "category": "Experience", "base_price": 80, "duration": 3},
]


class ActivitySearchInput(BaseModel):
    city: str = Field(description="City to search for activities")
    category: Optional[str] = Field(default=None, description="Activity category filter (e.g., 'Museum', 'Tour', 'Food')")


def generate_mock_activities(city: str, category: Optional[str] = None) -> List[dict]:
    city_activities = ACTIVITIES_BY_CITY.get(city, DEFAULT_ACTIVITIES)

    activities = []
    for activity in city_activities:
        if category and activity["category"].lower() != category.lower():
            continue

        price_variation = random.uniform(0.9, 1.1)

        act = {
            "id": str(uuid.uuid4()),
            "name": activity["name"],
            "city": city,
            "description": f"Experience {activity['name']} in {city}. A wonderful {activity['category'].lower()} activity for travelers.",
            "price": round(activity["base_price"] * price_variation, 2),
            "duration_hours": activity["duration"],
            "category": activity["category"],
        }
        activities.append(act)

    return activities


@tool("search_activities", args_schema=ActivitySearchInput)
def search_activities(city: str, category: Optional[str] = None) -> str:
    """Search for activities and attractions in a city."""
    activities = generate_mock_activities(city, category)

    if not activities:
        return f"No activities found in {city}" + (f" for category {category}" if category else "")

    result = f"Found {len(activities)} activities in {city}"
    if category:
        result += f" (category: {category})"
    result += ":\n\n"

    for i, activity in enumerate(activities, 1):
        result += f"{i}. {activity['name']} ({activity['category']})\n"
        result += f"   {activity['description']}\n"
        result += f"   Duration: {activity['duration_hours']} hours | Price: ${activity['price']}\n\n"

    return result


class ActivitySearchTool:
    @staticmethod
    def search(city: str, category: Optional[str] = None) -> List[dict]:
        return generate_mock_activities(city, category)
