const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface Itinerary {
  destination: string
  departure_city: string
  start_date: string
  end_date: string
  flights: Flight[]
  hotels: Hotel[]
  activities: Activity[]
  total_price: number
}

export interface Flight {
  id: string
  airline: string
  departure_city: string
  arrival_city: string
  departure_time: string
  arrival_time: string
  price: number
  flight_number: string
}

export interface Hotel {
  id: string
  name: string
  city: string
  rating: number
  price_per_night: number
  amenities: string[]
  check_in: string
  check_out: string
}

export interface Activity {
  id: string
  name: string
  city: string
  description: string
  price: number
  duration_hours: number
  category: string
}

export interface ChatResponse {
  message: string
  session_id: string
  itinerary?: Itinerary
  booking_ready: boolean
}

export interface Booking {
  id: string
  session_id: string
  itinerary: Itinerary
  user_name: string
  user_email: string
  confirmed_at: string
  status: string
}

export async function sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  })

  if (!response.ok) {
    throw new Error('Failed to send message')
  }

  return response.json()
}

export async function getItinerary(sessionId: string): Promise<Itinerary> {
  const response = await fetch(`${API_URL}/api/itinerary/${sessionId}`)

  if (!response.ok) {
    throw new Error('Failed to get itinerary')
  }

  return response.json()
}

export async function confirmBooking(
  sessionId: string,
  userName: string,
  userEmail: string
): Promise<{ booking_id: string; message: string; booking: Booking }> {
  const response = await fetch(`${API_URL}/api/booking/confirm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      user_name: userName,
      user_email: userEmail,
    }),
  })

  if (!response.ok) {
    throw new Error('Failed to confirm booking')
  }

  return response.json()
}

export async function getBookings(password: string): Promise<{ bookings: Booking[] }> {
  const response = await fetch(`${API_URL}/api/admin/bookings?password=${encodeURIComponent(password)}`)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Invalid admin password')
    }
    throw new Error('Failed to get bookings')
  }

  return response.json()
}

export async function adminQuery(
  query: string,
  password: string
): Promise<{ answer: string; sources: string[] }> {
  const response = await fetch(`${API_URL}/api/admin/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      password: password,
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Invalid admin password')
    }
    throw new Error('Failed to execute query')
  }

  return response.json()
}

export async function getNotifications(password: string): Promise<{ notifications: unknown[] }> {
  const response = await fetch(`${API_URL}/api/admin/notifications?password=${encodeURIComponent(password)}`)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Invalid admin password')
    }
    throw new Error('Failed to get notifications')
  }

  return response.json()
}

export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}
