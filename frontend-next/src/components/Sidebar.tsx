'use client';

import { Plane, Hotel, MapPin, X } from 'lucide-react';
import type { Preferences, Itinerary } from '@/lib/api';

interface SidebarProps {
  preferences: Preferences;
  itinerary: Itinerary;
  bookingId?: string | null;
  onConfirm: () => void;
  onRemoveItem?: (type: string, index: number) => void;
}

export default function Sidebar({
  preferences,
  itinerary,
  bookingId,
  onConfirm,
}: SidebarProps) {
  const hasItems =
    itinerary.flights.length > 0 ||
    itinerary.hotels.length > 0 ||
    itinerary.activities.length > 0;

  return (
    <div className="w-80 flex-shrink-0 flex flex-col gap-4 p-4 overflow-y-auto">
      {/* Preferences Card */}
      <div className="bg-card border border-border rounded-xl p-4">
        <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Your Preferences
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted">Destination</span>
            <span className="text-white">{preferences.destination || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">Origin</span>
            <span className="text-white">{preferences.origin || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">Dates</span>
            <span className="text-white">
              {preferences.start_date && preferences.end_date
                ? `${preferences.start_date} - ${preferences.end_date}`
                : '-'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">Budget</span>
            <span className="text-white">
              {preferences.budget ? `$${preferences.budget}` : '-'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">Style</span>
            <span className="text-white">{preferences.travel_style || '-'}</span>
          </div>
        </div>
      </div>

      {/* Itinerary Card */}
      <div className="bg-card border border-border rounded-xl p-4 flex-1">
        <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Your Itinerary
        </h3>

        {!hasItems ? (
          <p className="text-muted text-sm text-center py-8">No items yet</p>
        ) : (
          <div className="space-y-3">
            {/* Flights */}
            {itinerary.flights.map((flight, idx) => (
              <div
                key={`flight-${idx}`}
                className="bg-card-hover rounded-lg p-3 relative group"
              >
                <div className="flex items-center gap-2 text-accent text-xs font-medium mb-1">
                  <Plane size={12} />
                  FLIGHT
                </div>
                <div className="text-sm font-medium">
                  {flight.airline}: {flight.from} → {flight.to}
                </div>
                <div className="text-sm text-muted">${flight.price}</div>
              </div>
            ))}

            {/* Hotels */}
            {itinerary.hotels.map((hotel, idx) => (
              <div
                key={`hotel-${idx}`}
                className="bg-card-hover rounded-lg p-3 relative group"
              >
                <div className="flex items-center gap-2 text-accent text-xs font-medium mb-1">
                  <Hotel size={12} />
                  HOTEL
                </div>
                <div className="text-sm font-medium">{hotel.name}</div>
                <div className="text-sm text-muted">
                  ${hotel.price_per_night}/night
                </div>
              </div>
            ))}

            {/* Activities */}
            {itinerary.activities.map((activity, idx) => (
              <div
                key={`activity-${idx}`}
                className="bg-card-hover rounded-lg p-3 relative group"
              >
                <div className="flex items-center gap-2 text-accent text-xs font-medium mb-1">
                  <MapPin size={12} />
                  ACTIVITY
                </div>
                <div className="text-sm font-medium">{activity.name}</div>
                <div className="text-sm text-muted">${activity.price}</div>
              </div>
            ))}
          </div>
        )}

        {/* Total */}
        {hasItems && (
          <>
            <div className="mt-4 pt-3 border-t border-border">
              <div className="text-center text-xl font-bold">
                Total: ${itinerary.total_cost.toFixed(2)}
              </div>
            </div>

            {/* Confirm Button or Badge */}
            {itinerary.confirmed ? (
              <div className="mt-3">
                <div className="bg-success text-white text-center py-2 rounded-lg font-medium">
                  Booking Confirmed!
                </div>
                {bookingId && (
                  <div className="mt-2 bg-accent text-white text-center py-2 rounded-lg text-sm">
                    Ref: <span className="font-mono font-bold">{bookingId}</span>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={onConfirm}
                className="mt-3 w-full bg-success hover:bg-success/90 text-white py-3 rounded-lg font-medium transition-colors"
              >
                Confirm Booking
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}
