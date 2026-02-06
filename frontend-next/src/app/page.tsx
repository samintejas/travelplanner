'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import ChatMessage from '@/components/ChatMessage';
import Sidebar from '@/components/Sidebar';
import ConfirmModal from '@/components/ConfirmModal';
import {
  sendMessage,
  addToItinerary,
  getItinerary,
  saveCustomerInfo,
  type ChatResponse,
  type Preferences,
  type Itinerary,
} from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
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

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        "Welcome to Travel Concierge! I'm here to help you plan your perfect trip to **anywhere in the world**.\n\nTell me where you'd like to go, your budget, and travel dates, and I'll help you find flights, hotels, and activities.\n\nTry asking: \"I want to plan a trip to Japan\" or \"Help me visit Paris\"",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [bookingId, setBookingId] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<Preferences>(initialPreferences);
  const [itinerary, setItinerary] = useState<Itinerary>(initialItinerary);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    if (!sessionId) return;

    try {
      await addToItinerary(sessionId, type, id);
      const itin = await getItinerary(sessionId);
      setItinerary(itin);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Added ${id} to your itinerary!` },
      ]);
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  const handleConfirm = async (email: string, name?: string, phone?: string) => {
    if (!sessionId) return;

    try {
      await saveCustomerInfo(sessionId, email, name, phone);
      setShowConfirmModal(false);

      // Send confirmation message
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
    } catch (error) {
      console.error('Error confirming:', error);
    }

    setLoading(false);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
        <div className="text-xl font-semibold">
          Travel<span className="text-accent">Concierge</span>
        </div>
        <nav className="flex gap-4">
          <a href="/" className="text-white">
            Customer
          </a>
          <a href="/admin" className="text-muted hover:text-white transition-colors">
            Admin
          </a>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <ChatMessage
                key={idx}
                role={msg.role}
                content={msg.content}
                onAddItem={msg.role === 'assistant' ? handleAddItem : undefined}
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

        {/* Sidebar */}
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
    </div>
  );
}
