'use client';

import ReactMarkdown from 'react-markdown';
import { Plus, Plane, Hotel, MapPin } from 'lucide-react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  onAddItem?: (type: string, id: string) => void;
}

export default function ChatMessage({ role, content, onAddItem }: ChatMessageProps) {
  // Extract booking IDs from content - robust pattern matching
  const extractBookingIds = (text: string) => {
    const items: { type: string; id: string; label: string }[] = [];

    // Match patterns: FL001, (FL001), **FL001**, Flight ID: FL001, etc.
    const flightPattern = /\b(FL\d{3})\b/gi;
    const hotelPattern = /\b(HT\d{3})\b/gi;
    const activityPattern = /\b(AC\d{3})\b/gi;

    let match;
    while ((match = flightPattern.exec(text)) !== null) {
      const id = match[1].toUpperCase();
      if (!items.find((i) => i.id === id)) {
        items.push({ type: 'flight', id, label: `Add Flight ${id}` });
      }
    }

    while ((match = hotelPattern.exec(text)) !== null) {
      const id = match[1].toUpperCase();
      if (!items.find((i) => i.id === id)) {
        items.push({ type: 'hotel', id, label: `Add Hotel ${id}` });
      }
    }

    while ((match = activityPattern.exec(text)) !== null) {
      const id = match[1].toUpperCase();
      if (!items.find((i) => i.id === id)) {
        items.push({ type: 'activity', id, label: `Add Activity ${id}` });
      }
    }

    return items;
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'flight':
        return <Plane size={16} />;
      case 'hotel':
        return <Hotel size={16} />;
      case 'activity':
        return <MapPin size={16} />;
      default:
        return <Plus size={16} />;
    }
  };

  const getButtonStyle = (type: string) => {
    switch (type) {
      case 'flight':
        return 'bg-blue-600 hover:bg-blue-700 border-blue-500';
      case 'hotel':
        return 'bg-purple-600 hover:bg-purple-700 border-purple-500';
      case 'activity':
        return 'bg-green-600 hover:bg-green-700 border-green-500';
      default:
        return 'bg-accent hover:bg-accent-hover border-accent';
    }
  };

  const bookingItems = role === 'assistant' ? extractBookingIds(content) : [];

  const handleAddClick = (e: React.MouseEvent, type: string, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Button clicked - Adding item:', type, id);
    if (onAddItem) {
      onAddItem(type, id);
    }
  };

  return (
    <div
      className={`max-w-[85%] rounded-2xl px-4 py-3 ${
        role === 'user'
          ? 'ml-auto bg-accent text-white'
          : 'mr-auto bg-card border border-border'
      }`}
    >
      {role === 'assistant' ? (
        <div className="markdown-content">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      ) : (
        <p>{content}</p>
      )}

      {/* Booking action buttons - always show for assistant messages with IDs */}
      {bookingItems.length > 0 && onAddItem && (
        <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-border/50">
          <span className="w-full text-xs text-muted mb-1">Click to add to your itinerary:</span>
          {bookingItems.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={(e) => handleAddClick(e, item.type, item.id)}
              style={{ pointerEvents: 'auto' }}
              className={`flex items-center gap-2 px-4 py-2.5 ${getButtonStyle(item.type)} text-white rounded-lg text-sm font-semibold transition-all cursor-pointer border-2 shadow-lg hover:shadow-xl hover:scale-105 active:scale-95`}
            >
              {getIcon(item.type)}
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
