const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface ChatResponse {
  session_id: string;
  response: string;
  intent: string;
  preferences: Preferences;
  itinerary_summary: string;
  confirmed: boolean;
  booking_id: string | null;
}

export interface Preferences {
  destination: string | null;
  origin: string | null;
  start_date: string | null;
  end_date: string | null;
  budget: number | null;
  travel_style: string | null;
}

export interface ItineraryItem {
  id: string;
  airline?: string;
  from?: string;
  to?: string;
  departure?: string;
  arrival?: string;
  price: number;
  name?: string;
  city?: string;
  rating?: number;
  price_per_night?: number;
  amenities?: string[];
  description?: string;
  duration?: string;
}

export interface Itinerary {
  flights: ItineraryItem[];
  hotels: ItineraryItem[];
  activities: ItineraryItem[];
  total_cost: number;
  confirmed: boolean;
  summary?: string;
}

export interface Booking {
  booking_id: string;
  session_id: string;
  timestamp: string;
  status: string;
  customer_info: {
    email: string | null;
    name: string | null;
    phone: string | null;
  };
  preferences: Preferences;
  itinerary: Itinerary;
  total_cost: number;
  chat_summary: string;
}

export async function sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) throw new Error('Failed to send message');
  return res.json();
}

export async function addToItinerary(sessionId: string, itemType: string, itemId: string) {
  const res = await fetch(`${API_URL}/book`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, item_type: itemType, item_id: itemId }),
  });
  if (!res.ok) throw new Error('Failed to add item');
  return res.json();
}

export async function getItinerary(sessionId: string): Promise<Itinerary> {
  const res = await fetch(`${API_URL}/itinerary/${sessionId}`);
  if (!res.ok) throw new Error('Failed to get itinerary');
  return res.json();
}

export async function saveCustomerInfo(sessionId: string, email: string, name?: string, phone?: string) {
  const res = await fetch(`${API_URL}/customer-info`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, email, name, phone }),
  });
  if (!res.ok) throw new Error('Failed to save customer info');
  return res.json();
}

export async function getBookings(): Promise<{ bookings: Booking[]; total: number }> {
  const res = await fetch(`${API_URL}/admin/bookings`);
  if (!res.ok) throw new Error('Failed to get bookings');
  return res.json();
}

export async function updateBookingStatus(bookingId: string, status: string) {
  const res = await fetch(`${API_URL}/admin/booking/${bookingId}?status=${status}`, {
    method: 'PATCH',
  });
  if (!res.ok) throw new Error('Failed to update booking');
  return res.json();
}
