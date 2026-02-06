'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import type { Itinerary } from '@/lib/api';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (email: string, name?: string, phone?: string) => void;
  itinerary: Itinerary;
}

export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  itinerary,
}: ConfirmModalProps) {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    await onConfirm(email, name || undefined, phone || undefined);
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-xl font-semibold">Confirm Your Booking</h2>
          <button
            onClick={onClose}
            className="text-muted hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-4">
          {/* Booking Summary */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-muted uppercase mb-3">
              Booking Summary
            </h3>

            {itinerary.flights.length > 0 && (
              <div className="mb-3">
                <div className="text-sm font-medium text-accent mb-1">Flights</div>
                {itinerary.flights.map((f, i) => (
                  <div key={i} className="bg-card-hover rounded-lg p-2 mb-1 text-sm">
                    {f.airline}: {f.from} → {f.to} - ${f.price}
                  </div>
                ))}
              </div>
            )}

            {itinerary.hotels.length > 0 && (
              <div className="mb-3">
                <div className="text-sm font-medium text-accent mb-1">Hotels</div>
                {itinerary.hotels.map((h, i) => (
                  <div key={i} className="bg-card-hover rounded-lg p-2 mb-1 text-sm">
                    {h.name} - ${h.price_per_night}/night
                  </div>
                ))}
              </div>
            )}

            {itinerary.activities.length > 0 && (
              <div className="mb-3">
                <div className="text-sm font-medium text-accent mb-1">Activities</div>
                {itinerary.activities.map((a, i) => (
                  <div key={i} className="bg-card-hover rounded-lg p-2 mb-1 text-sm">
                    {a.name} - ${a.price}
                  </div>
                ))}
              </div>
            )}

            <div className="text-xl font-bold text-center mt-4 pt-3 border-t border-border">
              Total: ${itinerary.total_cost.toFixed(2)}
            </div>
          </div>

          {/* Customer Info Form */}
          <form onSubmit={handleSubmit}>
            <h3 className="text-sm font-semibold text-muted uppercase mb-3">
              Your Contact Information
            </h3>

            <div className="space-y-3">
              <div>
                <label className="block text-sm text-muted mb-1">
                  Email Address *
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                  className="w-full px-3 py-2 bg-card-hover border border-border rounded-lg focus:outline-none focus:border-accent"
                />
              </div>

              <div>
                <label className="block text-sm text-muted mb-1">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full px-3 py-2 bg-card-hover border border-border rounded-lg focus:outline-none focus:border-accent"
                />
              </div>

              <div>
                <label className="block text-sm text-muted mb-1">Phone Number</label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1 234 567 8900"
                  className="w-full px-3 py-2 bg-card-hover border border-border rounded-lg focus:outline-none focus:border-accent"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-3 bg-card-hover border border-border rounded-lg font-medium hover:bg-border transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!email || loading}
                className="flex-1 px-4 py-3 bg-success text-white rounded-lg font-medium hover:bg-success/90 transition-colors disabled:opacity-50"
              >
                {loading ? 'Confirming...' : 'Confirm Booking'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
