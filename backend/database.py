"""Database models and connection for Travel Concierge."""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://travel:travel123@localhost:5432/travel_concierge")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Session(Base):
    """Customer chat session."""
    __tablename__ = "sessions"

    id = Column(String(50), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    destination = Column(String(200), nullable=True)
    origin = Column(String(200), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    budget = Column(Float, nullable=True)
    travel_style = Column(String(50), nullable=True)
    confirmed = Column(Boolean, default=False)
    booking_id = Column(String(50), nullable=True)

    # Customer info
    customer_email = Column(String(200), nullable=True)
    customer_name = Column(String(200), nullable=True)
    customer_phone = Column(String(50), nullable=True)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    itinerary_items = relationship("ItineraryItem", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message in a session."""
    __tablename__ = "chat_messages"

    id = Column(String(50), primary_key=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class ItineraryItem(Base):
    """Item in a session's itinerary."""
    __tablename__ = "itinerary_items"

    id = Column(String(50), primary_key=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    item_type = Column(String(20), nullable=False)  # flight, hotel, activity
    item_id = Column(String(50), nullable=False)
    item_data = Column(JSON, nullable=False)
    price = Column(Float, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="itinerary_items")


class Booking(Base):
    """Confirmed booking."""
    __tablename__ = "bookings"

    id = Column(String(50), primary_key=True)  # TRV-XXXXXX
    session_id = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default="confirmed")  # confirmed, processing, completed, cancelled

    # Customer info
    customer_email = Column(String(200), nullable=True)
    customer_name = Column(String(200), nullable=True)
    customer_phone = Column(String(50), nullable=True)

    # Booking details
    destination = Column(String(200), nullable=True)
    preferences = Column(JSON, nullable=True)
    itinerary = Column(JSON, nullable=True)
    total_cost = Column(Float, default=0.0)
    chat_summary = Column(Text, nullable=True)


class Notification(Base):
    """Admin notification for new bookings."""
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True)
    booking_id = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
    data = Column(JSON, nullable=True)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
