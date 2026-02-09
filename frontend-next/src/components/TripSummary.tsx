'use client';

import { Plane, Hotel, MapPin, Calendar, DollarSign, CheckCircle } from 'lucide-react';
import type { Preferences, Itinerary } from '@/lib/api';

interface TripSummaryProps {
  preferences: Preferences;
  itinerary: Itinerary;
  bookingId?: string | null;
  onConfirm: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function TripSummary({
  preferences,
  itinerary,
  bookingId,
  onConfirm,
  isOpen,
  onClose,
}: TripSummaryProps) {
  if (!isOpen) return null;

  const hasItems =
    itinerary.flights.length > 0 ||
    itinerary.hotels.length > 0 ||
    itinerary.activities.length > 0;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">
              {itinerary.confirmed ? 'Booking Confirmed!' : 'Trip Summary'}
            </h2>
            <button
              onClick={onClose}
              className="text-muted hover:text-white text-2xl"
            >
              ×
            </button>
          </div>
          {preferences.destination && (
            <p className="text-muted mt-1">Your trip to {preferences.destination}</p>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Booking Reference */}
          {bookingId && (
            <div className="bg-success/20 border border-success/30 rounded-xl p-4 mb-6 text-center">
              <CheckCircle className="mx-auto text-success mb-2" size={32} />
              <div className="text-sm text-muted mb-1">Booking Reference</div>
              <div className="text-2xl font-mono font-bold text-success">{bookingId}</div>
              <p className="text-sm text-muted mt-2">
                Please save this reference number for your records
              </p>
            </div>
          )}

          {/* Trip Details */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-card-hover rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted text-sm mb-1">
                <MapPin size={14} />
                Destination
              </div>
              <div className="font-semibold">{preferences.destination || 'Not set'}</div>
            </div>
            <div className="bg-card-hover rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted text-sm mb-1">
                <Calendar size={14} />
                Dates
              </div>
              <div className="font-semibold">
                {preferences.start_date && preferences.end_date
                  ? `${preferences.start_date} - ${preferences.end_date}`
                  : 'Not set'}
              </div>
            </div>
            <div className="bg-card-hover rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted text-sm mb-1">
                <DollarSign size={14} />
                Budget
              </div>
              <div className="font-semibold">
                {preferences.budget ? `$${preferences.budget}` : 'Not set'}
              </div>
            </div>
            <div className="bg-card-hover rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted text-sm mb-1">
                Style
              </div>
              <div className="font-semibold">{preferences.travel_style || 'Not set'}</div>
            </div>
          </div>

          {/* Flights */}
          {itinerary.flights.length > 0 && (
            <div className="mb-6">
              <h3 className="flex items-center gap-2 text-lg font-semibold mb-3">
                <Plane className="text-accent" size={20} />
                Flights
              </h3>
              <div className="space-y-2">
                {itinerary.flights.map((flight, idx) => (
                  <div
                    key={idx}
                    className="bg-card-hover rounded-lg p-4 flex justify-between items-center"
                  >
                    <div>
                      <div className="font-medium">{flight.airline}</div>
                      <div className="text-sm text-muted">
                        {flight.from} → {flight.to}
                      </div>
                      <div className="text-xs text-muted">{flight.departure}</div>
                    </div>
                    <div className="text-lg font-bold text-accent">${flight.price}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Hotels */}
          {itinerary.hotels.length > 0 && (
            <div className="mb-6">
              <h3 className="flex items-center gap-2 text-lg font-semibold mb-3">
                <Hotel className="text-accent" size={20} />
                Hotels
              </h3>
              <div className="space-y-2">
                {itinerary.hotels.map((hotel, idx) => (
                  <div
                    key={idx}
                    className="bg-card-hover rounded-lg p-4 flex justify-between items-center"
                  >
                    <div>
                      <div className="font-medium">{hotel.name}</div>
                      <div className="text-sm text-muted">{hotel.city}</div>
                      {hotel.rating && (
                        <div className="text-xs text-yellow-500">
                          {'★'.repeat(Math.floor(hotel.rating))} {hotel.rating}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-accent">
                        ${hotel.price_per_night}/night
                      </div>
                      <div className="text-xs text-muted">3 nights = ${(hotel.price_per_night || 0) * 3}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Activities */}
          {itinerary.activities.length > 0 && (
            <div className="mb-6">
              <h3 className="flex items-center gap-2 text-lg font-semibold mb-3">
                <MapPin className="text-accent" size={20} />
                Activities
              </h3>
              <div className="space-y-2">
                {itinerary.activities.map((activity, idx) => (
                  <div
                    key={idx}
                    className="bg-card-hover rounded-lg p-4 flex justify-between items-center"
                  >
                    <div>
                      <div className="font-medium">{activity.name}</div>
                      <div className="text-sm text-muted">{activity.duration}</div>
                    </div>
                    <div className="text-lg font-bold text-accent">${activity.price}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Total */}
          {hasItems && (
            <div className="border-t border-border pt-4 mt-4">
              <div className="flex justify-between items-center text-xl">
                <span className="font-semibold">Total Cost</span>
                <span className="font-bold text-accent">
                  ${itinerary.total_cost.toFixed(2)}
                </span>
              </div>
            </div>
          )}

          {/* No items message */}
          {!hasItems && (
            <div className="text-center py-8 text-muted">
              <p>No items in your itinerary yet.</p>
              <p className="text-sm mt-1">Add flights, hotels, or activities to build your trip.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-card-hover border border-border rounded-lg font-medium hover:bg-border transition-colors"
          >
            {itinerary.confirmed ? 'Close' : 'Continue Planning'}
          </button>
          {hasItems && !itinerary.confirmed && (
            <button
              onClick={onConfirm}
              className="flex-1 px-4 py-3 bg-success hover:bg-success/90 text-white rounded-lg font-medium transition-colors"
            >
              Confirm & Book
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
