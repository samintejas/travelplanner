'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Send, Loader2, LogOut, Plane, Hotel, MapPin, Plus, MessageSquare, CheckCircle, Clock } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import ChatMessage from '@/components/ChatMessage';
import ConfirmModal from '@/components/ConfirmModal';
import TripSummary from '@/components/TripSummary';
import { useAuth } from '@/lib/auth';
import {
  sendMessage,
  addToItinerary,
  getItinerary,
  saveCustomerInfo,
  getSessions,
  getSessionDetails,
  type Preferences,
  type Itinerary,
  type SessionInfo,
} from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface BookableItem {
  type: 'flight' | 'hotel' | 'activity';
  id: string;
  label: string;
}

const initialPreferences: Preferences = {
  destination: null,
  origin: null,
  start_date: null,
  end_date: null,
  budget: null,
  travel_style: null,
};

const initialItinerary: Itinerary = {
  flights: [],
  hotels: [],
  activities: [],
  total_cost: 0,
  confirmed: false,
};

const welcomeMessage: Message = {
  role: 'assistant',
  content:
    "Welcome to Travel Concierge! I'm here to help you plan your perfect trip to **anywhere in the world**.\n\nTell me where you'd like to go, your budget, and travel dates, and I'll help you find flights, hotels, and activities.\n\nTry asking: \"I want to plan a trip to Paris\" or \"Show me flights to Tokyo\"",
};

// Extract bookable IDs from text
function extractBookableItems(text: string): BookableItem[] {
  const items: BookableItem[] = [];

  // Match FL001, HT001, AC001 patterns
  const flightMatches = text.match(/FL\d{3}/gi) || [];
  const hotelMatches = text.match(/HT\d{3}/gi) || [];
  const activityMatches = text.match(/AC\d{3}/gi) || [];

  flightMatches.forEach(id => {
    const normalizedId = id.toUpperCase();
    if (!items.find(i => i.id === normalizedId)) {
      items.push({ type: 'flight', id: normalizedId, label: `Flight ${normalizedId}` });
    }
  });

  hotelMatches.forEach(id => {
    const normalizedId = id.toUpperCase();
    if (!items.find(i => i.id === normalizedId)) {
      items.push({ type: 'hotel', id: normalizedId, label: `Hotel ${normalizedId}` });
    }
  });

  activityMatches.forEach(id => {
    const normalizedId = id.toUpperCase();
    if (!items.find(i => i.id === normalizedId)) {
      items.push({ type: 'activity', id: normalizedId, label: `Activity ${normalizedId}` });
    }
  });

  return items;
}

export default function ChatPage() {
  const { user, role, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [addingItem, setAddingItem] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [bookingId, setBookingId] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<Preferences>(initialPreferences);
  const [itinerary, setItinerary] = useState<Itinerary>(initialItinerary);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showTripSummary, setShowTripSummary] = useState(false);
  const [bookableItems, setBookableItems] = useState<BookableItem[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Extract bookable items from the last assistant message
  useEffect(() => {
    const lastAssistantMessage = [...messages].reverse().find(m => m.role === 'assistant');
    if (lastAssistantMessage) {
      const items = extractBookableItems(lastAssistantMessage.content);
      setBookableItems(items);
    }
  }, [messages]);

  // Fetch sessions
  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data.sessions);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
    setSessionsLoading(false);
  };

  useEffect(() => {
    fetchSessions();
  }, [sessionId]);

  // Load session from localStorage on mount
  useEffect(() => {
    const storedSessionId = localStorage.getItem('travel_session_id');
    if (storedSessionId) {
      loadSession(storedSessionId);
    }
  }, []);

  // Save session to localStorage when it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('travel_session_id', sessionId);
    }
  }, [sessionId]);

  const loadSession = async (id: string) => {
    try {
      const details = await getSessionDetails(id);
      setSessionId(id);
      setPreferences(details.preferences);
      setItinerary(details.itinerary);

      if (details.chat_history.length > 0) {
        setMessages(details.chat_history.map(m => ({
          role: m.role,
          content: m.content
        })));
      } else {
        setMessages([welcomeMessage]);
      }

      if (details.confirmed) {
        setBookingId(details.id);
      }
    } catch (error) {
      console.error('Error loading session:', error);
      handleNewTrip();
    }
  };

  const handleSelectSession = (id: string) => {
    loadSession(id);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendMessage(userMessage, sessionId || undefined);
      setSessionId(response.session_id);
      setPreferences(response.preferences);

      if (response.confirmed && response.booking_id) {
        setBookingId(response.booking_id);
      }

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.response },
      ]);

      // Refresh itinerary
      if (response.session_id) {
        const itin = await getItinerary(response.session_id);
        setItinerary(itin);
      }

      // Refresh sessions list
      fetchSessions();
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ]);
    }

    setLoading(false);
  };

  const handleAddItem = async (type: string, id: string) => {
    console.log('handleAddItem called:', type, id, 'sessionId:', sessionId);

    if (!sessionId) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Please start a conversation first by telling me about your trip.' },
      ]);
      return;
    }

    setAddingItem(id);

    try {
      const result = await addToItinerary(sessionId, type, id);
      console.log('Add result:', result);
      const itin = await getItinerary(sessionId);
      setItinerary(itin);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `✅ **${id} added to your itinerary!**\n\nTotal: **$${itin.total_cost.toFixed(2)}**`
        },
      ]);
      // Remove added item from bookable items
      setBookableItems(prev => prev.filter(item => item.id !== id));
    } catch (error) {
      console.error('Error adding item:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Failed to add ${id}. Please try again.` },
      ]);
    }

    setAddingItem(null);
  };

  const handleConfirm = async (email: string, name?: string, phone?: string) => {
    if (!sessionId) return;

    try {
      await saveCustomerInfo(sessionId, email, name, phone);
      setShowConfirmModal(false);

      setMessages((prev) => [
        ...prev,
        { role: 'user', content: 'Please confirm my booking' },
      ]);
      setLoading(true);

      const response = await sendMessage('Please confirm my booking', sessionId);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.response },
      ]);

      if (response.booking_id) {
        setBookingId(response.booking_id);
      }

      const itin = await getItinerary(sessionId);
      setItinerary(itin);
      fetchSessions();
    } catch (error) {
      console.error('Error confirming:', error);
    }

    setLoading(false);
  };

  const handleNewTrip = () => {
    setSessionId(null);
    setMessages([welcomeMessage]);
    setPreferences(initialPreferences);
    setItinerary(initialItinerary);
    setBookingId(null);
    setBookableItems([]);
    localStorage.removeItem('travel_session_id');
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const getItemIcon = (type: string) => {
    switch (type) {
      case 'flight': return <Plane size={18} />;
      case 'hotel': return <Hotel size={18} />;
      case 'activity': return <MapPin size={18} />;
      default: return null;
    }
  };

  const getItemColor = (type: string) => {
    switch (type) {
      case 'flight': return 'bg-blue-600 hover:bg-blue-700 border-blue-400';
      case 'hotel': return 'bg-purple-600 hover:bg-purple-700 border-purple-400';
      case 'activity': return 'bg-green-600 hover:bg-green-700 border-green-400';
      default: return 'bg-accent hover:bg-accent-hover border-accent';
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
        <div className="text-xl font-semibold">
          Travel<span className="text-accent">Concierge</span>
        </div>
        <div className="flex items-center gap-4">
          {role === 'admin' && (
            <a href="/admin" className="text-muted hover:text-white transition-colors text-sm">
              Admin Panel
            </a>
          )}
          <div className="flex items-center gap-3 ml-2 pl-4 border-l border-border">
            <span className="text-sm text-muted">
              {user?.name || user?.email}
            </span>
            <button
              onClick={handleLogout}
              className="p-2 text-muted hover:text-white transition-colors"
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Session History */}
        <div className="w-64 bg-card border-r border-border flex flex-col h-full">
          <div className="p-4 border-b border-border">
            <button
              onClick={handleNewTrip}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg font-medium transition-colors"
            >
              <Plus size={18} />
              New Trip
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            <div className="p-2">
              <div className="text-xs font-semibold text-muted uppercase px-2 py-2">
                Recent Sessions
              </div>

              {sessionsLoading ? (
                <div className="text-center text-muted py-4 text-sm">Loading...</div>
              ) : sessions.length === 0 ? (
                <div className="text-center text-muted py-4 text-sm">No sessions yet</div>
              ) : (
                <div className="space-y-1">
                  {sessions.map((session) => (
                    <button
                      key={session.id}
                      onClick={() => handleSelectSession(session.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        sessionId === session.id
                          ? 'bg-accent/20 border border-accent/30'
                          : 'hover:bg-card-hover'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <MessageSquare size={14} className="text-muted" />
                        <span className="font-medium text-sm truncate flex-1">
                          {session.destination || 'New Trip'}
                        </span>
                        {session.confirmed ? (
                          <CheckCircle size={14} className="text-green-500" />
                        ) : (
                          <Clock size={14} className="text-muted" />
                        )}
                      </div>
                      <div className="text-xs text-muted mt-1 pl-6">
                        {session.message_count} messages
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <ChatMessage
                key={idx}
                role={msg.role}
                content={msg.content}
                onAddItem={handleAddItem}
              />
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-muted">
                <Loader2 className="animate-spin" size={20} />
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Action Buttons - Outside of messages */}
          {bookableItems.length > 0 && !itinerary.confirmed && (
            <div className="px-4 py-3 border-t border-border bg-card/80 backdrop-blur">
              <div className="text-xs text-muted mb-2 font-medium uppercase tracking-wide">
                Click to add to your itinerary:
              </div>
              <div className="flex flex-wrap gap-2">
                {bookableItems.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleAddItem(item.type, item.id)}
                    disabled={addingItem === item.id}
                    className={`flex items-center gap-2 px-4 py-2.5 ${getItemColor(item.type)} text-white rounded-lg font-semibold transition-all border-2 shadow-md hover:shadow-lg hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100`}
                  >
                    {addingItem === item.id ? (
                      <Loader2 className="animate-spin" size={18} />
                    ) : (
                      getItemIcon(item.type)
                    )}
                    <span>Add {item.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t border-border bg-card">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Tell me about your dream trip..."
                className="flex-1 px-4 py-3 bg-card-hover border border-border rounded-xl focus:outline-none focus:border-accent"
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-medium transition-colors disabled:opacity-50"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Right Sidebar - Itinerary */}
        <div className="border-l border-border bg-card">
          <Sidebar
            preferences={preferences}
            itinerary={itinerary}
            bookingId={bookingId}
            onConfirm={() => setShowConfirmModal(true)}
          />
        </div>
      </div>

      {/* Confirm Modal */}
      <ConfirmModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={handleConfirm}
        itinerary={itinerary}
      />

      {/* Trip Summary Modal */}
      <TripSummary
        preferences={preferences}
        itinerary={itinerary}
        bookingId={bookingId}
        onConfirm={() => {
          setShowTripSummary(false);
          setShowConfirmModal(true);
        }}
        isOpen={showTripSummary}
        onClose={() => setShowTripSummary(false)}
      />
    </div>
  );
}
