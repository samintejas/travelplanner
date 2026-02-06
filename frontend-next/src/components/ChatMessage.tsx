'use client';

import ReactMarkdown from 'react-markdown';
import { Plus } from 'lucide-react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  onAddItem?: (type: string, id: string) => void;
}

export default function ChatMessage({ role, content, onAddItem }: ChatMessageProps) {
  // Extract booking IDs from content
  const extractBookingIds = (text: string) => {
    const patterns = {
      flight: /\(FL\d+\)/g,
      hotel: /\(HT\d+\)/g,
      activity: /\(AC\d+\)/g,
    };

    const items: { type: string; id: string }[] = [];

    for (const [type, pattern] of Object.entries(patterns)) {
      const matches = text.match(pattern);
      if (matches) {
        matches.forEach((match) => {
          const id = match.replace(/[()]/g, '');
          if (!items.find((i) => i.id === id)) {
            items.push({ type, id });
          }
        });
      }
    }

    return items;
  };

  const bookingItems = role === 'assistant' ? extractBookingIds(content) : [];

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

      {/* Booking action buttons */}
      {bookingItems.length > 0 && onAddItem && (
        <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-border">
          {bookingItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onAddItem(item.type, item.id)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-accent/20 hover:bg-accent/30 text-accent rounded-full text-sm font-medium transition-colors"
            >
              <Plus size={14} />
              Add {item.id}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
