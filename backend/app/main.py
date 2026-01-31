from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import json
import asyncio
from typing import Dict, Any
import uuid
from datetime import datetime

from .config import get_settings, Settings
from .models import (
    ChatRequest,
    ChatResponse,
    BookingConfirmRequest,
    AdminQueryRequest,
    AdminQueryResponse,
    Booking,
)
from .agents.graph import TravelGraph
from .rag.chroma_client import ChromaClient
from .rag.retriever import TravelRetriever
from .rag.destination_loader import load_destination_documents
from .services.notifications import NotificationService

app = FastAPI(
    title="Travel Concierge AI",
    description="AI-powered travel planning assistant",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
travel_graph = TravelGraph()
bookings_db: Dict[str, Booking] = {}


@app.on_event("startup")
async def startup_event():
    """Load destination knowledge on startup."""
    try:
        chroma = ChromaClient()
        load_destination_documents(chroma)
    except Exception as e:
        print(f"Warning: Could not load destination documents: {e}")


def get_chroma_client(settings: Settings = Depends(get_settings)) -> ChromaClient:
    return ChromaClient(host=settings.chroma_host, port=settings.chroma_port)


def get_retriever(chroma: ChromaClient = Depends(get_chroma_client)) -> TravelRetriever:
    return TravelRetriever(chroma)


@app.get("/")
async def root():
    return {"message": "Welcome to Travel Concierge AI", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return AI response."""
    try:
        result = travel_graph.process_message(
            session_id=request.session_id,
            message=request.message,
        )

        # Store conversation in ChromaDB
        try:
            state = travel_graph.get_session_state(request.session_id)
            if state:
                chroma = ChromaClient()
                messages = [
                    {"role": "user" if hasattr(m, "type") and m.type == "human" else "assistant", "content": m.content}
                    for m in state.get("messages", [])
                ]
                chroma.add_conversation(request.session_id, messages)
        except Exception as e:
            print(f"Warning: Could not store conversation: {e}")

        return ChatResponse(
            message=result["response"],
            session_id=request.session_id,
            itinerary=result.get("itinerary"),
            booking_ready=result.get("booking_ready", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/stream")
async def chat_stream(session_id: str, message: str):
    """Stream chat response using Server-Sent Events."""

    async def generate():
        try:
            result = travel_graph.process_message(
                session_id=session_id,
                message=message,
            )

            # Simulate streaming by sending chunks
            response_text = result["response"]
            words = response_text.split()

            for i, word in enumerate(words):
                chunk = word + " " if i < len(words) - 1 else word
                yield {
                    "event": "message",
                    "data": json.dumps({"chunk": chunk, "done": False}),
                }
                await asyncio.sleep(0.05)

            # Send final message with full data
            yield {
                "event": "message",
                "data": json.dumps({
                    "chunk": "",
                    "done": True,
                    "itinerary": result.get("itinerary"),
                    "booking_ready": result.get("booking_ready", False),
                }),
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(generate())


@app.get("/api/itinerary/{session_id}")
async def get_itinerary(session_id: str):
    """Get the current itinerary for a session."""
    state = travel_graph.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    itinerary = state.get("itinerary")
    if not itinerary:
        raise HTTPException(status_code=404, detail="No itinerary found for this session")

    return itinerary


@app.post("/api/booking/confirm")
async def confirm_booking(request: BookingConfirmRequest):
    """Confirm a booking."""
    state = travel_graph.get_session_state(request.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    if not state.get("itinerary"):
        raise HTTPException(status_code=400, detail="No itinerary to book")

    result = travel_graph.confirm_booking(
        session_id=request.session_id,
        user_name=request.user_name,
        user_email=request.user_email,
    )

    # Store booking
    booking_id = str(uuid.uuid4())
    booking = Booking(
        id=booking_id,
        session_id=request.session_id,
        itinerary=state["itinerary"],
        user_name=request.user_name,
        user_email=request.user_email,
        confirmed_at=datetime.utcnow(),
        status="confirmed",
    )
    bookings_db[booking_id] = booking

    # Store in ChromaDB
    try:
        chroma = ChromaClient()
        chroma.add_booking(booking_id, {
            "session_id": request.session_id,
            "user_name": request.user_name,
            "user_email": request.user_email,
            "destination": state["itinerary"].get("destination", "Unknown"),
            "status": "confirmed",
        })
    except Exception as e:
        print(f"Warning: Could not store booking in ChromaDB: {e}")

    return {
        "booking_id": booking_id,
        "message": result["response"],
        "booking": booking,
    }


@app.get("/api/admin/bookings")
async def get_bookings(password: str, settings: Settings = Depends(get_settings)):
    """Get all bookings (admin only)."""
    if password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    return {"bookings": list(bookings_db.values())}


@app.get("/api/admin/notifications")
async def get_notifications(password: str, settings: Settings = Depends(get_settings)):
    """Get admin notifications."""
    if password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    return {"notifications": NotificationService.get_notifications()}


@app.post("/api/admin/query", response_model=AdminQueryResponse)
async def admin_query(
    request: AdminQueryRequest,
    settings: Settings = Depends(get_settings),
):
    """Query conversations and bookings using RAG."""
    if request.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    try:
        chroma = ChromaClient()
        retriever = TravelRetriever(chroma)

        # Search conversations
        conversations = retriever.retrieve_relevant_conversations(request.query)
        bookings = retriever.retrieve_bookings(request.query)

        # Format results
        sources = []
        context_parts = []

        for conv in conversations:
            sources.append(f"Session: {conv['session_id']}")
            context_parts.append(f"[{conv['role']}]: {conv['content']}")

        for booking in bookings:
            sources.append(f"Booking: {booking['metadata'].get('user_name', 'Unknown')}")
            context_parts.append(booking['content'])

        # Generate answer using LLM
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        context = "\n".join(context_parts) if context_parts else "No relevant data found."

        response = llm.invoke(
            f"Based on the following travel booking data, answer this question: {request.query}\n\nData:\n{context}"
        )

        return AdminQueryResponse(
            answer=response.content,
            sources=list(set(sources)),
        )

    except Exception as e:
        return AdminQueryResponse(
            answer=f"Error processing query: {str(e)}",
            sources=[],
        )


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session state."""
    state = travel_graph.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "current_agent": state.get("current_agent"),
        "preferences": state.get("preferences"),
        "preferences_complete": state.get("preferences_complete"),
        "has_itinerary": state.get("itinerary") is not None,
        "booking_confirmed": state.get("booking_confirmed"),
    }
