"""Hardcoded travel data for testing."""

FLIGHTS = [
    {
        "id": "FL001",
        "airline": "SkyWay Airlines",
        "from": "New York (JFK)",
        "to": "Paris (CDG)",
        "departure": "2025-03-15 08:00",
        "arrival": "2025-03-15 20:30",
        "price": 650,
        "class": "economy"
    },
    {
        "id": "FL002",
        "airline": "SkyWay Airlines",
        "from": "New York (JFK)",
        "to": "Paris (CDG)",
        "departure": "2025-03-15 14:00",
        "arrival": "2025-03-16 02:30",
        "price": 580,
        "class": "economy"
    },
    {
        "id": "FL003",
        "airline": "Atlantic Air",
        "from": "New York (JFK)",
        "to": "London (LHR)",
        "departure": "2025-03-15 10:00",
        "arrival": "2025-03-15 22:00",
        "price": 520,
        "class": "economy"
    },
    {
        "id": "FL004",
        "airline": "Pacific Wings",
        "from": "Los Angeles (LAX)",
        "to": "Tokyo (NRT)",
        "departure": "2025-03-20 11:00",
        "arrival": "2025-03-21 15:00",
        "price": 890,
        "class": "economy"
    },
    {
        "id": "FL005",
        "airline": "Euro Express",
        "from": "Paris (CDG)",
        "to": "Rome (FCO)",
        "departure": "2025-03-18 09:00",
        "arrival": "2025-03-18 11:15",
        "price": 180,
        "class": "economy"
    },
]

HOTELS = [
    {
        "id": "HT001",
        "name": "Hotel Le Marais",
        "city": "Paris",
        "rating": 4.5,
        "price_per_night": 180,
        "amenities": ["WiFi", "Breakfast", "Gym"],
        "description": "Charming boutique hotel in the heart of Le Marais district."
    },
    {
        "id": "HT002",
        "name": "Grand Plaza Paris",
        "city": "Paris",
        "rating": 4.8,
        "price_per_night": 320,
        "amenities": ["WiFi", "Breakfast", "Gym", "Spa", "Pool"],
        "description": "Luxury hotel near the Champs-Élysées."
    },
    {
        "id": "HT003",
        "name": "London Bridge Inn",
        "city": "London",
        "rating": 4.2,
        "price_per_night": 150,
        "amenities": ["WiFi", "Breakfast"],
        "description": "Cozy hotel with views of the Thames."
    },
    {
        "id": "HT004",
        "name": "Sakura Garden Hotel",
        "city": "Tokyo",
        "rating": 4.6,
        "price_per_night": 200,
        "amenities": ["WiFi", "Breakfast", "Onsen", "Garden"],
        "description": "Traditional Japanese hospitality meets modern comfort."
    },
    {
        "id": "HT005",
        "name": "Roma Centro B&B",
        "city": "Rome",
        "rating": 4.3,
        "price_per_night": 120,
        "amenities": ["WiFi", "Breakfast"],
        "description": "Family-run B&B steps from the Colosseum."
    },
]

ACTIVITIES = [
    {
        "id": "AC001",
        "name": "Eiffel Tower Skip-the-Line Tour",
        "city": "Paris",
        "duration": "3 hours",
        "price": 65,
        "description": "Skip the crowds with priority access to the Eiffel Tower."
    },
    {
        "id": "AC002",
        "name": "Louvre Museum Guided Tour",
        "city": "Paris",
        "duration": "4 hours",
        "price": 85,
        "description": "Expert-led tour of the world's most famous museum."
    },
    {
        "id": "AC003",
        "name": "London Eye & Thames Cruise",
        "city": "London",
        "duration": "2.5 hours",
        "price": 55,
        "description": "Panoramic views from the London Eye plus a river cruise."
    },
    {
        "id": "AC004",
        "name": "Tokyo Food Walking Tour",
        "city": "Tokyo",
        "duration": "3 hours",
        "price": 95,
        "description": "Taste your way through Tokyo's best street food."
    },
    {
        "id": "AC005",
        "name": "Colosseum Underground Tour",
        "city": "Rome",
        "duration": "3.5 hours",
        "price": 75,
        "description": "Explore the hidden underground chambers of the Colosseum."
    },
]

TRAVEL_GUIDES = {
    "Paris": {
        "best_time": "April to June, September to November",
        "currency": "Euro (EUR)",
        "language": "French",
        "tips": [
            "Book museum tickets in advance to skip lines",
            "Metro is the fastest way to get around",
            "Most shops close on Sundays",
            "Tipping is not required but appreciated"
        ],
        "must_see": ["Eiffel Tower", "Louvre", "Notre-Dame", "Montmartre", "Champs-Élysées"]
    },
    "London": {
        "best_time": "May to September",
        "currency": "British Pound (GBP)",
        "language": "English",
        "tips": [
            "Get an Oyster card for public transport",
            "Many museums are free",
            "Weather is unpredictable - bring layers",
            "Stand on the right on escalators"
        ],
        "must_see": ["Big Ben", "Tower of London", "British Museum", "Buckingham Palace", "Hyde Park"]
    },
    "Tokyo": {
        "best_time": "March to May, September to November",
        "currency": "Japanese Yen (JPY)",
        "language": "Japanese",
        "tips": [
            "Get a Suica/Pasmo card for trains",
            "Cash is still widely used",
            "Be quiet on public transport",
            "Remove shoes when entering homes/some restaurants"
        ],
        "must_see": ["Shibuya Crossing", "Senso-ji Temple", "Meiji Shrine", "Tokyo Skytree", "Tsukiji Market"]
    },
    "Rome": {
        "best_time": "April to June, September to October",
        "currency": "Euro (EUR)",
        "language": "Italian",
        "tips": [
            "Book Vatican and Colosseum tickets well in advance",
            "Siesta time (1-4pm) means many shops close",
            "Drink from the public fountains - water is fresh",
            "Dress modestly for churches"
        ],
        "must_see": ["Colosseum", "Vatican City", "Trevi Fountain", "Pantheon", "Roman Forum"]
    }
}


def search_flights(origin: str = None, destination: str = None, date: str = None) -> list:
    """Search flights with optional filters."""
    results = FLIGHTS.copy()
    if origin:
        results = [f for f in results if origin.lower() in f["from"].lower()]
    if destination:
        results = [f for f in results if destination.lower() in f["to"].lower()]
    if date:
        results = [f for f in results if date in f["departure"]]
    return results


def search_hotels(city: str = None, max_price: float = None) -> list:
    """Search hotels with optional filters."""
    results = HOTELS.copy()
    if city:
        results = [h for h in results if city.lower() in h["city"].lower()]
    if max_price:
        results = [h for h in results if h["price_per_night"] <= max_price]
    return results


def search_activities(city: str = None) -> list:
    """Search activities by city."""
    if city:
        return [a for a in ACTIVITIES if city.lower() in a["city"].lower()]
    return ACTIVITIES.copy()


def get_travel_guide(city: str) -> dict:
    """Get travel guide for a city."""
    for guide_city, guide in TRAVEL_GUIDES.items():
        if city.lower() in guide_city.lower():
            return {"city": guide_city, **guide}
    return None
