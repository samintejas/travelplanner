from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    message: str
    session_id: str
    itinerary: Optional["Itinerary"] = None
    booking_ready: bool = False


class Flight(BaseModel):
    id: str
    airline: str
    departure_city: str
    arrival_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    flight_number: str


class Hotel(BaseModel):
    id: str
    name: str
    city: str
    rating: float
    price_per_night: float
    amenities: List[str]
    check_in: date
    check_out: date


class Activity(BaseModel):
    id: str
    name: str
    city: str
    description: str
    price: float
    duration_hours: float
    category: str


class Itinerary(BaseModel):
    id: str
    session_id: str
    destination: str
    start_date: date
    end_date: date
    flights: List[Flight] = []
    hotels: List[Hotel] = []
    activities: List[Activity] = []
    total_price: float = 0.0
    status: str = "draft"


class Booking(BaseModel):
    id: str
    session_id: str
    itinerary: Itinerary
    user_name: str
    user_email: str
    confirmed_at: datetime
    status: str = "confirmed"


class BookingConfirmRequest(BaseModel):
    session_id: str
    user_name: str
    user_email: str


class AdminQueryRequest(BaseModel):
    query: str
    password: str


class AdminQueryResponse(BaseModel):
    answer: str
    sources: List[str] = []
