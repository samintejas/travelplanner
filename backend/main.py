"""FastAPI backend for Travel Concierge AI with PostgreSQL persistence."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
from datetime import datetime
import uuid
import os

from sqlalchemy.orm import Session as DBSession
from database import init_db, get_db, Session, ChatMessage, ItineraryItem, Booking, Notification
from agents import CoordinatorAgent, TravelPreferences, Itinerary
from data import FLIGHTS, HOTELS, ACTIVITIES
from llm import chat_with_context, detect_intent
from rag import get_rag


app = FastAPI(title="Travel Concierge AI")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class BookingRequest(BaseModel):
    session_id: str
    item_type: str
    item_id: str


class CustomerInfo(BaseModel):
    session_id: str
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None


class AdminQuery(BaseModel):
    query: str
    session_id: Optional[str] = None


def generate_booking_id() -> str:
    """Generate a unique booking reference number."""
    import random
    import string
    prefix = "TRV"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


def get_or_create_session(session_id: Optional[str], db: DBSession) -> Session:
    """Get existing session or create a new one."""
    if session_id:
        session = db.query(Session).filter(Session.id == session_id).first()
        if session:
            return session

    new_id = str(uuid.uuid4())[:8]
    session = Session(id=new_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def session_to_preferences(session: Session) -> TravelPreferences:
    """Convert DB session to TravelPreferences."""
    return TravelPreferences(
        destination=session.destination,
        origin=session.origin,
        start_date=session.start_date,
        end_date=session.end_date,
        budget=session.budget,
        travel_style=session.travel_style
    )


def get_session_itinerary(session: Session, db: DBSession) -> dict:
    """Get itinerary data from session."""
    items = db.query(ItineraryItem).filter(ItineraryItem.session_id == session.id).all()

    flights = []
    hotels = []
    activities = []
    total_cost = 0.0

    for item in items:
        if item.item_type == "flight":
            flights.append(item.item_data)
        elif item.item_type == "hotel":
            hotels.append(item.item_data)
        elif item.item_type == "activity":
            activities.append(item.item_data)
        total_cost += item.price

    return {
        "flights": flights,
        "hotels": hotels,
        "activities": activities,
        "total_cost": total_cost,
        "confirmed": session.confirmed
    }


def get_chat_history(session_id: str, db: DBSession) -> list[dict]:
    """Get chat history for a session."""
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).all()

    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in messages]


# ============ Customer Endpoints ============

@app.post("/api/chat")
async def chat(msg: ChatMessageRequest, db: DBSession = Depends(get_db)):
    """Main chat endpoint for customers."""
    session = get_or_create_session(msg.session_id, db)
    preferences = session_to_preferences(session)
    itinerary_data = get_session_itinerary(session, db)

    # Save user message
    user_msg = ChatMessage(
        id=str(uuid.uuid4())[:12],
        session_id=session.id,
        role="user",
        content=msg.message
    )
    db.add(user_msg)
    db.commit()

    # Get chat history
    chat_history = get_chat_history(session.id, db)

    # Detect intent
    intent = detect_intent(msg.message)

    # Prepare data for LLM
    prefs_dict = {
        "destination": preferences.destination,
        "origin": preferences.origin,
        "start_date": preferences.start_date,
        "end_date": preferences.end_date,
        "budget": preferences.budget,
        "travel_style": preferences.travel_style,
    }

    # Get LLM response
    response, extracted_prefs = chat_with_context(
        msg.message,
        chat_history[:-1],
        prefs_dict,
        itinerary_data
    )

    # Update session preferences
    if extracted_prefs.get("destination"):
        session.destination = extracted_prefs["destination"]
    if extracted_prefs.get("origin"):
        session.origin = extracted_prefs["origin"]
    if extracted_prefs.get("start_date"):
        session.start_date = extracted_prefs["start_date"]
    if extracted_prefs.get("end_date"):
        session.end_date = extracted_prefs["end_date"]
    if extracted_prefs.get("budget"):
        session.budget = extracted_prefs["budget"]
    if extracted_prefs.get("travel_style"):
        session.travel_style = extracted_prefs["travel_style"]

    # Handle booking confirmation
    booking_id = None
    if intent == "confirm" and itinerary_data["total_cost"] > 0:
        booking_id = generate_booking_id()
        session.booking_id = booking_id
        session.confirmed = True

        # Create booking record
        booking = Booking(
            id=booking_id,
            session_id=session.id,
            status="confirmed",
            customer_email=session.customer_email,
            customer_name=session.customer_name,
            customer_phone=session.customer_phone,
            destination=session.destination,
            preferences=prefs_dict,
            itinerary=itinerary_data,
            total_cost=itinerary_data["total_cost"],
            chat_summary=f"Customer had {len(chat_history)} messages"
        )
        db.add(booking)

        # Create notification
        notification = Notification(
            id=str(uuid.uuid4())[:12],
            booking_id=booking_id,
            data={"destination": session.destination, "total_cost": itinerary_data["total_cost"]}
        )
        db.add(notification)

        # Add conversation to ChromaDB for RAG
        try:
            rag = get_rag()
            rag.add_conversation(session.id, chat_history)
        except Exception as e:
            print(f"Error adding conversation to ChromaDB: {e}")

    # Save assistant message
    assistant_msg = ChatMessage(
        id=str(uuid.uuid4())[:12],
        session_id=session.id,
        role="assistant",
        content=response
    )
    db.add(assistant_msg)
    db.commit()

    # Generate itinerary summary
    coordinator = CoordinatorAgent()
    itinerary_obj = Itinerary(preferences=preferences)
    itinerary_obj.flights = itinerary_data["flights"]
    itinerary_obj.hotels = itinerary_data["hotels"]
    itinerary_obj.activities = itinerary_data["activities"]
    itinerary_obj.total_cost = itinerary_data["total_cost"]
    itinerary_obj.confirmed = session.confirmed

    return {
        "session_id": session.id,
        "response": response,
        "intent": intent,
        "preferences": {
            "destination": session.destination,
            "origin": session.origin,
            "start_date": session.start_date,
            "end_date": session.end_date,
            "budget": session.budget,
            "travel_style": session.travel_style,
        },
        "itinerary_summary": coordinator.generate_itinerary_summary(itinerary_obj),
        "confirmed": session.confirmed,
        "booking_id": booking_id or session.booking_id,
    }


@app.post("/api/book")
async def add_to_itinerary(booking: BookingRequest, db: DBSession = Depends(get_db)):
    """Add an item to the itinerary."""
    session = db.query(Session).filter(Session.id == booking.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    item = None
    price = 0.0

    if booking.item_type == "flight":
        item = next((f for f in FLIGHTS if f["id"] == booking.item_id), None)
        if item:
            price = item["price"]
    elif booking.item_type == "hotel":
        item = next((h for h in HOTELS if h["id"] == booking.item_id), None)
        if item:
            price = item["price_per_night"] * 3  # 3 nights default
    elif booking.item_type == "activity":
        item = next((a for a in ACTIVITIES if a["id"] == booking.item_id), None)
        if item:
            price = item["price"]

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Add to itinerary
    itinerary_item = ItineraryItem(
        id=str(uuid.uuid4())[:12],
        session_id=session.id,
        item_type=booking.item_type,
        item_id=booking.item_id,
        item_data=item,
        price=price
    )
    db.add(itinerary_item)
    db.commit()

    # Get updated itinerary
    itinerary_data = get_session_itinerary(session, db)

    coordinator = CoordinatorAgent()
    itinerary_obj = Itinerary(preferences=session_to_preferences(session))
    itinerary_obj.flights = itinerary_data["flights"]
    itinerary_obj.hotels = itinerary_data["hotels"]
    itinerary_obj.activities = itinerary_data["activities"]
    itinerary_obj.total_cost = itinerary_data["total_cost"]

    return {
        "success": True,
        "message": f"Added {booking.item_type} to your itinerary!",
        "itinerary_summary": coordinator.generate_itinerary_summary(itinerary_obj),
    }


@app.post("/api/customer-info")
async def save_customer_info(info: CustomerInfo, db: DBSession = Depends(get_db)):
    """Save customer contact info before confirmation."""
    session = db.query(Session).filter(Session.id == info.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.customer_email = info.email
    session.customer_name = info.name
    session.customer_phone = info.phone
    db.commit()

    return {"success": True, "message": "Customer info saved"}


@app.get("/api/itinerary/{session_id}")
async def get_itinerary(session_id: str, db: DBSession = Depends(get_db)):
    """Get current itinerary for a session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    itinerary_data = get_session_itinerary(session, db)

    coordinator = CoordinatorAgent()
    itinerary_obj = Itinerary(preferences=session_to_preferences(session))
    itinerary_obj.flights = itinerary_data["flights"]
    itinerary_obj.hotels = itinerary_data["hotels"]
    itinerary_obj.activities = itinerary_data["activities"]
    itinerary_obj.total_cost = itinerary_data["total_cost"]
    itinerary_obj.confirmed = session.confirmed

    return {
        **itinerary_data,
        "summary": coordinator.generate_itinerary_summary(itinerary_obj),
    }


# ============ Admin Endpoints ============

@app.get("/api/admin/notifications")
async def get_notifications(db: DBSession = Depends(get_db)):
    """Get all booking notifications for admin."""
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).all()

    result = []
    for n in notifications:
        booking = db.query(Booking).filter(Booking.id == n.booking_id).first()
        if booking:
            result.append({
                "id": n.id,
                "booking_id": n.booking_id,
                "timestamp": n.created_at.isoformat(),
                "read": n.read,
                "preferences": booking.preferences,
                "itinerary": booking.itinerary,
                "chat_summary": booking.chat_summary,
            })

    return {"notifications": result}


@app.get("/api/admin/bookings")
async def get_all_bookings(db: DBSession = Depends(get_db)):
    """Get all confirmed bookings for admin."""
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()

    result = []
    for b in bookings:
        result.append({
            "booking_id": b.id,
            "session_id": b.session_id,
            "timestamp": b.created_at.isoformat(),
            "status": b.status,
            "customer_info": {
                "email": b.customer_email,
                "name": b.customer_name,
                "phone": b.customer_phone,
            },
            "preferences": b.preferences,
            "itinerary": b.itinerary,
            "total_cost": b.total_cost,
            "chat_summary": b.chat_summary,
        })

    return {"bookings": result, "total": len(result)}


@app.get("/api/admin/booking/{booking_id}")
async def get_booking_details(booking_id: str, db: DBSession = Depends(get_db)):
    """Get detailed booking information."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    chat_history = get_chat_history(booking.session_id, db)

    return {
        "booking_id": booking.id,
        "session_id": booking.session_id,
        "timestamp": booking.created_at.isoformat(),
        "status": booking.status,
        "customer_info": {
            "email": booking.customer_email,
            "name": booking.customer_name,
            "phone": booking.customer_phone,
        },
        "preferences": booking.preferences,
        "itinerary": booking.itinerary,
        "total_cost": booking.total_cost,
        "chat_history": chat_history,
    }


@app.patch("/api/admin/booking/{booking_id}")
async def update_booking_status(booking_id: str, status: str, db: DBSession = Depends(get_db)):
    """Update booking status."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = status
    booking.updated_at = datetime.now()
    db.commit()

    return {"success": True, "booking_id": booking_id, "status": status}


@app.get("/api/admin/sessions")
async def get_all_sessions(db: DBSession = Depends(get_db)):
    """Get all active sessions for admin."""
    sessions = db.query(Session).order_by(Session.created_at.desc()).all()

    result = []
    for s in sessions:
        message_count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        result.append({
            "id": s.id,
            "created_at": s.created_at.isoformat(),
            "destination": s.destination,
            "confirmed": s.confirmed,
            "message_count": message_count,
        })

    return {"sessions": result}


@app.get("/api/admin/session/{session_id}")
async def get_session_details(session_id: str, db: DBSession = Depends(get_db)):
    """Get detailed session info for admin."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_history = get_chat_history(session_id, db)
    itinerary_data = get_session_itinerary(session, db)

    return {
        "id": session.id,
        "created_at": session.created_at.isoformat(),
        "preferences": {
            "destination": session.destination,
            "origin": session.origin,
            "start_date": session.start_date,
            "end_date": session.end_date,
            "budget": session.budget,
            "travel_style": session.travel_style,
        },
        "itinerary": itinerary_data,
        "chat_history": chat_history,
        "confirmed": session.confirmed,
    }


@app.post("/api/admin/query")
async def admin_query(query: AdminQuery, db: DBSession = Depends(get_db)):
    """Admin can query over sessions and travel data using RAG."""
    rag = get_rag()

    # Search conversations in ChromaDB
    conversation_results = rag.search_conversations(query.query, query.session_id)

    # Search travel data
    travel_results = rag.search(query.query)

    # If querying specific session, get details
    session_info = None
    if query.session_id:
        session = db.query(Session).filter(Session.id == query.session_id).first()
        if session:
            session_info = {
                "destination": session.destination,
                "budget": session.budget,
                "travel_style": session.travel_style,
            }

    return {
        "query": query.query,
        "session_id": query.session_id,
        "session_info": session_info,
        "conversation_results": conversation_results[:5],
        "travel_results": travel_results[:5],
    }


# ============ Static Files & Frontend ============

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.get("/")
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/admin")
async def serve_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")


app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="static")


# ============ Startup ============

@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG on startup."""
    print("Initializing database...")
    init_db()
    print("Database initialized!")

    if os.getenv("OPENAI_API_KEY"):
        print("Initializing RAG with ChromaDB...")
        try:
            rag = get_rag()
            rag.index_data()
            print("RAG initialized!")
        except Exception as e:
            print(f"Warning: RAG initialization failed: {e}")
    else:
        print("Warning: OPENAI_API_KEY not set. LLM features disabled.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
