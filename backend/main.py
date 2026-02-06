"""FastAPI backend for Travel Concierge AI."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
from datetime import datetime
import uuid

from agents import (
    CoordinatorAgent,
    TravelPreferences,
    Itinerary,
)
from data import search_flights, search_hotels, search_activities, FLIGHTS, HOTELS, ACTIVITIES
from llm import chat_with_context, detect_intent
from rag import get_rag
import os


app = FastAPI(title="Travel Concierge AI")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
sessions: dict = {}
admin_notifications: list = []
confirmed_bookings: dict = {}  # booking_id -> booking details


def generate_booking_id() -> str:
    """Generate a unique booking reference number."""
    import random
    import string
    prefix = "TRV"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class BookingRequest(BaseModel):
    session_id: str
    item_type: str  # flight, hotel, activity
    item_id: str


class CustomerInfo(BaseModel):
    session_id: str
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None


class AdminQuery(BaseModel):
    query: str
    session_id: Optional[str] = None  # Optional: query specific session


# ============ Session Management ============

def get_or_create_session(session_id: Optional[str]) -> tuple[str, dict]:
    """Get existing session or create a new one."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    new_id = str(uuid.uuid4())[:8]
    sessions[new_id] = {
        "id": new_id,
        "created_at": datetime.now().isoformat(),
        "preferences": TravelPreferences(),
        "itinerary": Itinerary(preferences=TravelPreferences()),
        "chat_history": [],
        "coordinator": CoordinatorAgent(),
        "confirmed": False,
        "customer_info": None,  # Will be set before confirmation
        "booking_id": None,  # Generated on confirmation
    }
    return new_id, sessions[new_id]


# ============ Customer Endpoints ============

@app.post("/api/chat")
async def chat(msg: ChatMessage):
    """Main chat endpoint for customers - powered by OpenAI with RAG."""
    session_id, session = get_or_create_session(msg.session_id)
    coordinator = session["coordinator"]
    preferences = session["preferences"]
    itinerary = session["itinerary"]

    # Store user message
    session["chat_history"].append({
        "role": "user",
        "content": msg.message,
        "timestamp": datetime.now().isoformat()
    })

    # Detect intent
    intent = detect_intent(msg.message)

    # Prepare preferences dict for LLM
    prefs_dict = {
        "destination": preferences.destination,
        "origin": preferences.origin,
        "start_date": preferences.start_date,
        "end_date": preferences.end_date,
        "budget": preferences.budget,
        "travel_style": preferences.travel_style,
    }

    # Prepare itinerary dict for LLM
    itin_dict = {
        "flights": itinerary.flights,
        "hotels": itinerary.hotels,
        "activities": itinerary.activities,
        "total_cost": itinerary.total_cost,
    }

    # Get LLM response with RAG context
    response, extracted_prefs = chat_with_context(
        msg.message,
        session["chat_history"][:-1],  # Exclude current message (already added)
        prefs_dict,
        itin_dict
    )

    # Update preferences from LLM extraction
    if extracted_prefs.get("destination"):
        preferences.destination = extracted_prefs["destination"]
    if extracted_prefs.get("origin"):
        preferences.origin = extracted_prefs["origin"]
    if extracted_prefs.get("start_date"):
        preferences.start_date = extracted_prefs["start_date"]
    if extracted_prefs.get("end_date"):
        preferences.end_date = extracted_prefs["end_date"]
    if extracted_prefs.get("budget"):
        preferences.budget = extracted_prefs["budget"]
    if extracted_prefs.get("travel_style"):
        preferences.travel_style = extracted_prefs["travel_style"]

    # Handle booking confirmation
    if intent == "confirm" and (itinerary.flights or itinerary.hotels or itinerary.activities):
        # Generate booking ID
        booking_id = generate_booking_id()
        session["booking_id"] = booking_id
        session["confirmed"] = True
        itinerary.confirmed = True

        # Create confirmed booking record
        booking_record = {
            "booking_id": booking_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "status": "confirmed",
            "customer_info": session.get("customer_info"),
            "preferences": {
                "destination": preferences.destination,
                "origin": preferences.origin,
                "dates": f"{preferences.start_date} - {preferences.end_date}",
                "budget": preferences.budget,
                "style": preferences.travel_style,
            },
            "itinerary": {
                "flights": itinerary.flights,
                "hotels": itinerary.hotels,
                "activities": itinerary.activities,
                "total_cost": itinerary.total_cost,
            },
            "chat_summary": _summarize_chat(session["chat_history"]),
        }

        # Store in confirmed bookings
        confirmed_bookings[booking_id] = booking_record

        # Notify admin
        admin_notifications.append(booking_record)

    # Store assistant response
    session["chat_history"].append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })

    return {
        "session_id": session_id,
        "response": response,
        "intent": intent,
        "preferences": {
            "destination": preferences.destination,
            "origin": preferences.origin,
            "start_date": preferences.start_date,
            "end_date": preferences.end_date,
            "budget": preferences.budget,
            "travel_style": preferences.travel_style,
        },
        "itinerary_summary": coordinator.generate_itinerary_summary(itinerary),
        "confirmed": session["confirmed"],
        "booking_id": session.get("booking_id"),
    }


@app.post("/api/book")
async def add_to_itinerary(booking: BookingRequest):
    """Add an item to the itinerary."""
    if booking.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[booking.session_id]
    itinerary = session["itinerary"]

    item = None
    if booking.item_type == "flight":
        item = next((f for f in FLIGHTS if f["id"] == booking.item_id), None)
        if item:
            itinerary.flights.append(item)
            itinerary.total_cost += item["price"]
    elif booking.item_type == "hotel":
        item = next((h for h in HOTELS if h["id"] == booking.item_id), None)
        if item:
            itinerary.hotels.append(item)
            # Assume 3 nights by default
            itinerary.total_cost += item["price_per_night"] * 3
    elif booking.item_type == "activity":
        item = next((a for a in ACTIVITIES if a["id"] == booking.item_id), None)
        if item:
            itinerary.activities.append(item)
            itinerary.total_cost += item["price"]

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    coordinator = session["coordinator"]
    return {
        "success": True,
        "message": f"Added {booking.item_type} to your itinerary!",
        "itinerary_summary": coordinator.generate_itinerary_summary(itinerary),
    }


@app.post("/api/customer-info")
async def save_customer_info(info: CustomerInfo):
    """Save customer contact info before confirmation."""
    if info.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[info.session_id]["customer_info"] = {
        "email": info.email,
        "name": info.name,
        "phone": info.phone,
    }

    return {"success": True, "message": "Customer info saved"}


@app.get("/api/itinerary/{session_id}")
async def get_itinerary(session_id: str):
    """Get current itinerary for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    itinerary = session["itinerary"]
    coordinator = session["coordinator"]

    return {
        "flights": itinerary.flights,
        "hotels": itinerary.hotels,
        "activities": itinerary.activities,
        "total_cost": itinerary.total_cost,
        "confirmed": itinerary.confirmed,
        "summary": coordinator.generate_itinerary_summary(itinerary),
    }


# ============ Admin Endpoints ============

@app.get("/api/admin/notifications")
async def get_notifications():
    """Get all booking notifications for admin."""
    return {"notifications": admin_notifications}


@app.get("/api/admin/bookings")
async def get_all_bookings():
    """Get all confirmed bookings for admin."""
    return {
        "bookings": list(confirmed_bookings.values()),
        "total": len(confirmed_bookings),
    }


@app.get("/api/admin/booking/{booking_id}")
async def get_booking_details(booking_id: str):
    """Get detailed booking information."""
    if booking_id not in confirmed_bookings:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking = confirmed_bookings[booking_id]

    # Get full chat history from session if available
    session_id = booking.get("session_id")
    chat_history = []
    if session_id and session_id in sessions:
        chat_history = sessions[session_id]["chat_history"]

    return {
        **booking,
        "chat_history": chat_history,
    }


@app.patch("/api/admin/booking/{booking_id}")
async def update_booking_status(booking_id: str, status: str):
    """Update booking status (confirmed, processing, completed, cancelled)."""
    if booking_id not in confirmed_bookings:
        raise HTTPException(status_code=404, detail="Booking not found")

    confirmed_bookings[booking_id]["status"] = status
    confirmed_bookings[booking_id]["updated_at"] = datetime.now().isoformat()

    return {"success": True, "booking_id": booking_id, "status": status}


@app.get("/api/admin/sessions")
async def get_all_sessions():
    """Get all active sessions for admin."""
    return {
        "sessions": [
            {
                "id": s["id"],
                "created_at": s["created_at"],
                "destination": s["preferences"].destination,
                "confirmed": s["confirmed"],
                "message_count": len(s["chat_history"]),
            }
            for s in sessions.values()
        ]
    }


@app.get("/api/admin/session/{session_id}")
async def get_session_details(session_id: str):
    """Get detailed session info for admin (RAG over conversation)."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    return {
        "id": session["id"],
        "created_at": session["created_at"],
        "preferences": {
            "destination": session["preferences"].destination,
            "origin": session["preferences"].origin,
            "start_date": session["preferences"].start_date,
            "end_date": session["preferences"].end_date,
            "budget": session["preferences"].budget,
            "travel_style": session["preferences"].travel_style,
        },
        "itinerary": {
            "flights": session["itinerary"].flights,
            "hotels": session["itinerary"].hotels,
            "activities": session["itinerary"].activities,
            "total_cost": session["itinerary"].total_cost,
            "confirmed": session["itinerary"].confirmed,
        },
        "chat_history": session["chat_history"],
        "confirmed": session["confirmed"],
    }


@app.post("/api/admin/query")
async def admin_query(query: AdminQuery):
    """Admin can query over sessions and travel data (RAG)."""
    query_lower = query.query.lower()
    results = []

    # Query specific session
    if query.session_id and query.session_id in sessions:
        session = sessions[query.session_id]
        chat_text = " ".join([m["content"] for m in session["chat_history"]])

        # Search in chat history
        relevant_messages = [
            m for m in session["chat_history"]
            if any(word in m["content"].lower() for word in query_lower.split())
        ]

        return {
            "query": query.query,
            "session_id": query.session_id,
            "relevant_messages": relevant_messages,
            "preferences": {
                "destination": session["preferences"].destination,
                "budget": session["preferences"].budget,
                "travel_style": session["preferences"].travel_style,
            },
            "answer": _generate_admin_answer(query.query, session),
        }

    # Query across all sessions
    for sid, session in sessions.items():
        for msg in session["chat_history"]:
            if any(word in msg["content"].lower() for word in query_lower.split()):
                results.append({
                    "session_id": sid,
                    "message": msg,
                    "destination": session["preferences"].destination,
                })

    # Query travel data
    travel_data_results = _search_travel_data(query.query)

    return {
        "query": query.query,
        "session_results": results[:10],
        "travel_data": travel_data_results,
        "total_sessions": len(sessions),
        "confirmed_bookings": sum(1 for s in sessions.values() if s["confirmed"]),
    }


# ============ Helper Functions ============

def _extract_preferences(message: str, prefs: TravelPreferences):
    """Extract travel preferences from user message."""
    message_lower = message.lower()

    # Destinations
    destinations = {
        'paris': 'Paris', 'london': 'London', 'tokyo': 'Tokyo',
        'rome': 'Rome', 'new york': 'New York', 'los angeles': 'Los Angeles'
    }
    for key, value in destinations.items():
        if key in message_lower:
            prefs.destination = value
            break

    # Origins
    origins = ['new york', 'los angeles', 'chicago', 'miami', 'boston']
    for origin in origins:
        if f"from {origin}" in message_lower:
            prefs.origin = origin.title()
            break

    # Travel style
    if any(word in message_lower for word in ['budget', 'cheap', 'affordable']):
        prefs.travel_style = 'budget'
    elif any(word in message_lower for word in ['luxury', 'premium', 'high-end']):
        prefs.travel_style = 'luxury'
    elif any(word in message_lower for word in ['moderate', 'mid-range']):
        prefs.travel_style = 'moderate'

    # Budget (simple extraction)
    import re
    budget_match = re.search(r'\$(\d+(?:,\d+)?)', message)
    if budget_match:
        prefs.budget = float(budget_match.group(1).replace(',', ''))


def _summarize_chat(chat_history: list) -> str:
    """Create a summary of chat for admin notification."""
    if not chat_history:
        return "No conversation recorded."

    user_messages = [m["content"] for m in chat_history if m["role"] == "user"]
    return f"Customer had {len(chat_history)} messages. Key requests: " + "; ".join(user_messages[:3])


def _search_travel_data(query: str) -> dict:
    """Search travel data based on query."""
    query_lower = query.lower()
    results = {"flights": [], "hotels": [], "activities": []}

    # Check for city mentions
    cities = ['paris', 'london', 'tokyo', 'rome']
    target_city = None
    for city in cities:
        if city in query_lower:
            target_city = city.title()
            break

    if target_city:
        results["flights"] = search_flights(destination=target_city)
        results["hotels"] = search_hotels(city=target_city)
        results["activities"] = search_activities(city=target_city)

    return results


def _generate_admin_answer(query: str, session: dict) -> str:
    """Generate an answer for admin query about a session."""
    query_lower = query.lower()
    prefs = session["preferences"]
    itinerary = session["itinerary"]

    if "budget" in query_lower:
        return f"Customer's budget: ${prefs.budget if prefs.budget else 'Not specified'}. Current itinerary total: ${itinerary.total_cost:.2f}"

    if "destination" in query_lower:
        return f"Customer is planning a trip to {prefs.destination or 'destination not yet selected'}."

    if "style" in query_lower or "preference" in query_lower:
        return f"Travel style: {prefs.travel_style or 'Not specified'}. Looking for {', '.join(prefs.interests) if prefs.interests else 'general travel'}."

    if "status" in query_lower or "confirmed" in query_lower:
        status = "confirmed" if session["confirmed"] else "in progress"
        return f"Booking status: {status}. Total items: {len(itinerary.flights)} flights, {len(itinerary.hotels)} hotels, {len(itinerary.activities)} activities."

    return f"Session for {prefs.destination or 'unknown destination'}. {len(session['chat_history'])} messages exchanged."


# ============ Static Files & Frontend ============

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.get("/")
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/admin")
async def serve_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")


# Mount static files (CSS, JS)
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="static")


# ============ Startup ============

@app.on_event("startup")
async def startup_event():
    """Initialize RAG on startup."""
    if os.getenv("OPENAI_API_KEY"):
        print("Initializing RAG with OpenAI embeddings...")
        try:
            rag = get_rag()
            rag.index_data()
            print("RAG initialized successfully!")
        except Exception as e:
            print(f"Warning: RAG initialization failed: {e}")
            print("Falling back to web search only.")
    else:
        print("Warning: OPENAI_API_KEY not set. LLM features disabled.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
