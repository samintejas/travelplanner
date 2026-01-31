from datetime import datetime, timedelta
from typing import List, Optional
import random
import uuid
from langchain.tools import tool
from pydantic import BaseModel, Field


AIRLINES = ["United Airlines", "Delta", "American Airlines", "JetBlue", "Southwest", "Air France", "British Airways", "Lufthansa", "ANA", "JAL"]
MOCK_ROUTES = {
    ("New York", "Paris"): {"base_price": 450, "duration_hours": 7.5},
    ("New York", "London"): {"base_price": 400, "duration_hours": 7},
    ("New York", "Tokyo"): {"base_price": 850, "duration_hours": 14},
    ("New York", "Osaka"): {"base_price": 900, "duration_hours": 14.5},
    ("Los Angeles", "Paris"): {"base_price": 550, "duration_hours": 11},
    ("Los Angeles", "Tokyo"): {"base_price": 650, "duration_hours": 11.5},
    ("Los Angeles", "Osaka"): {"base_price": 680, "duration_hours": 12},
    ("Los Angeles", "Kyoto"): {"base_price": 700, "duration_hours": 12.5},
    ("Chicago", "London"): {"base_price": 480, "duration_hours": 8},
    ("Chicago", "Tokyo"): {"base_price": 780, "duration_hours": 13},
    ("San Francisco", "Tokyo"): {"base_price": 600, "duration_hours": 11},
    ("San Francisco", "Osaka"): {"base_price": 620, "duration_hours": 11.5},
    ("Miami", "Paris"): {"base_price": 520, "duration_hours": 9},
    ("Boston", "London"): {"base_price": 380, "duration_hours": 6.5},
    ("Seattle", "Tokyo"): {"base_price": 580, "duration_hours": 10},
    ("Seattle", "Osaka"): {"base_price": 600, "duration_hours": 10.5},
}


class FlightSearchInput(BaseModel):
    departure_city: str = Field(description="City of departure")
    arrival_city: str = Field(description="Destination city")
    departure_date: str = Field(description="Date of departure in YYYY-MM-DD format")
    return_date: Optional[str] = Field(default=None, description="Return date in YYYY-MM-DD format for round trips")


def generate_mock_flights(
    departure_city: str,
    arrival_city: str,
    departure_date: str,
    num_options: int = 3,
) -> List[dict]:
    route = (departure_city, arrival_city)
    reverse_route = (arrival_city, departure_city)

    if route in MOCK_ROUTES:
        route_info = MOCK_ROUTES[route]
    elif reverse_route in MOCK_ROUTES:
        route_info = MOCK_ROUTES[reverse_route]
    else:
        route_info = {"base_price": 500, "duration_hours": 8}

    flights = []
    base_date = datetime.strptime(departure_date, "%Y-%m-%d")

    for i in range(num_options):
        departure_hour = random.choice([6, 8, 10, 14, 16, 20])
        departure_time = base_date.replace(hour=departure_hour, minute=random.randint(0, 59))
        duration = route_info["duration_hours"] + random.uniform(-0.5, 0.5)
        arrival_time = departure_time + timedelta(hours=duration)
        price_variation = random.uniform(0.8, 1.3)

        flight = {
            "id": str(uuid.uuid4()),
            "airline": random.choice(AIRLINES),
            "departure_city": departure_city,
            "arrival_city": arrival_city,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat(),
            "price": round(route_info["base_price"] * price_variation, 2),
            "flight_number": f"{random.choice(['UA', 'DL', 'AA', 'JB', 'SW', 'AF', 'BA', 'LH'])}{random.randint(100, 999)}",
        }
        flights.append(flight)

    return sorted(flights, key=lambda x: x["price"])


@tool("search_flights", args_schema=FlightSearchInput)
def search_flights(
    departure_city: str,
    arrival_city: str,
    departure_date: str,
    return_date: Optional[str] = None,
) -> str:
    """Search for available flights between two cities on a specific date."""
    outbound_flights = generate_mock_flights(departure_city, arrival_city, departure_date)

    result = f"Found {len(outbound_flights)} outbound flights from {departure_city} to {arrival_city} on {departure_date}:\n\n"
    for i, flight in enumerate(outbound_flights, 1):
        dep_time = datetime.fromisoformat(flight["departure_time"]).strftime("%H:%M")
        arr_time = datetime.fromisoformat(flight["arrival_time"]).strftime("%H:%M")
        result += f"{i}. {flight['airline']} {flight['flight_number']}\n"
        result += f"   Departure: {dep_time} -> Arrival: {arr_time}\n"
        result += f"   Price: ${flight['price']}\n\n"

    if return_date:
        return_flights = generate_mock_flights(arrival_city, departure_city, return_date)
        result += f"\nFound {len(return_flights)} return flights from {arrival_city} to {departure_city} on {return_date}:\n\n"
        for i, flight in enumerate(return_flights, 1):
            dep_time = datetime.fromisoformat(flight["departure_time"]).strftime("%H:%M")
            arr_time = datetime.fromisoformat(flight["arrival_time"]).strftime("%H:%M")
            result += f"{i}. {flight['airline']} {flight['flight_number']}\n"
            result += f"   Departure: {dep_time} -> Arrival: {arr_time}\n"
            result += f"   Price: ${flight['price']}\n\n"

    return result


class FlightSearchTool:
    @staticmethod
    def search(
        departure_city: str,
        arrival_city: str,
        departure_date: str,
        return_date: Optional[str] = None,
    ) -> List[dict]:
        outbound = generate_mock_flights(departure_city, arrival_city, departure_date)
        result = {"outbound": outbound}
        if return_date:
            result["return"] = generate_mock_flights(arrival_city, departure_city, return_date)
        return result
