'use client';

import { useState, useEffect } from 'react';
import { Plane, Hotel, MapPin, CheckCircle, XCircle, Clock } from 'lucide-react';
import { getBookings, updateBookingStatus, type Booking } from '@/lib/api';

export default function AdminPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    confirmed: 0,
    completed: 0,
    revenue: 0,
  });

  const fetchBookings = async () => {
    try {
      const data = await getBookings();
      setBookings(data.bookings);

      // Calculate stats
      const confirmed = data.bookings.filter((b) => b.status === 'confirmed').length;
      const completed = data.bookings.filter((b) => b.status === 'completed').length;
      const revenue = data.bookings.reduce((sum, b) => sum + (b.total_cost || 0), 0);

      setStats({
        total: data.total,
        confirmed,
        completed,
        revenue,
      });
    } catch (error) {
      console.error('Error fetching bookings:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchBookings();
    const interval = setInterval(fetchBookings, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStatusUpdate = async (bookingId: string, status: string) => {
    try {
      await updateBookingStatus(bookingId, status);
      fetchBookings();
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <Clock className="text-yellow-500" size={16} />;
      case 'completed':
        return <CheckCircle className="text-green-500" size={16} />;
      case 'cancelled':
        return <XCircle className="text-red-500" size={16} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-yellow-500/20 text-yellow-500';
      case 'completed':
        return 'bg-green-500/20 text-green-500';
      case 'cancelled':
        return 'bg-red-500/20 text-red-500';
      default:
        return 'bg-gray-500/20 text-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
        <div className="text-xl font-semibold">
          Travel<span className="text-accent">Concierge</span>{' '}
          <span className="text-muted font-normal">Admin</span>
        </div>
        <nav className="flex gap-4">
          <a href="/" className="text-muted hover:text-white transition-colors">
            Customer
          </a>
          <a href="/admin" className="text-white">
            Admin
          </a>
        </nav>
      </header>

      <div className="p-6">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-accent">{stats.total}</div>
            <div className="text-sm text-muted">Total Bookings</div>
          </div>
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-yellow-500">{stats.confirmed}</div>
            <div className="text-sm text-muted">Confirmed</div>
          </div>
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-green-500">{stats.completed}</div>
            <div className="text-sm text-muted">Completed</div>
          </div>
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-accent">
              ${stats.revenue.toFixed(0)}
            </div>
            <div className="text-sm text-muted">Total Revenue</div>
          </div>
        </div>

        {/* Bookings List */}
        <h2 className="text-xl font-semibold mb-4">Confirmed Bookings</h2>

        {loading ? (
          <div className="text-center text-muted py-12">Loading...</div>
        ) : bookings.length === 0 ? (
          <div className="text-center text-muted py-12 bg-card border border-border rounded-xl">
            No bookings yet
          </div>
        ) : (
          <div className="space-y-4">
            {bookings.map((booking) => (
              <div
                key={booking.booking_id}
                className="bg-card border border-border rounded-xl p-5"
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-accent font-semibold">
                      {booking.booking_id}
                    </span>
                    <span className="text-muted text-sm">
                      {new Date(booking.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                      booking.status
                    )}`}
                  >
                    {getStatusIcon(booking.status)}
                    <span className="ml-1">{booking.status}</span>
                  </span>
                </div>

                {/* Customer Info */}
                <div className="mb-4 pb-4 border-b border-border">
                  <div className="text-xs text-muted uppercase mb-1">Customer</div>
                  {booking.customer_info?.email ? (
                    <div>
                      <div className="font-medium">
                        {booking.customer_info.name || 'N/A'}
                      </div>
                      <div className="text-sm text-muted">
                        {booking.customer_info.email}
                      </div>
                      {booking.customer_info.phone && (
                        <div className="text-sm text-muted">
                          {booking.customer_info.phone}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-muted">No customer info</div>
                  )}
                </div>

                {/* Destination */}
                <div className="mb-4">
                  <span className="text-muted">Destination: </span>
                  <span className="font-medium">
                    {booking.preferences?.destination || 'N/A'}
                  </span>
                </div>

                {/* Items */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  {/* Flights */}
                  <div>
                    <div className="flex items-center gap-2 text-accent text-xs font-medium mb-2">
                      <Plane size={14} />
                      FLIGHTS
                    </div>
                    {booking.itinerary?.flights?.map((f: any, i: number) => (
                      <div key={i} className="bg-card-hover rounded-lg p-2 mb-1 text-sm">
                        <div className="font-medium">{f.airline}</div>
                        <div className="text-muted">
                          {f.from} → {f.to}
                        </div>
                        <div className="text-accent">${f.price}</div>
                      </div>
                    )) || <div className="text-muted text-sm">None</div>}
                  </div>

                  {/* Hotels */}
                  <div>
                    <div className="flex items-center gap-2 text-accent text-xs font-medium mb-2">
                      <Hotel size={14} />
                      HOTELS
                    </div>
                    {booking.itinerary?.hotels?.map((h: any, i: number) => (
                      <div key={i} className="bg-card-hover rounded-lg p-2 mb-1 text-sm">
                        <div className="font-medium">{h.name}</div>
                        <div className="text-muted">{h.city}</div>
                        <div className="text-accent">${h.price_per_night}/night</div>
                      </div>
                    )) || <div className="text-muted text-sm">None</div>}
                  </div>

                  {/* Activities */}
                  <div>
                    <div className="flex items-center gap-2 text-accent text-xs font-medium mb-2">
                      <MapPin size={14} />
                      ACTIVITIES
                    </div>
                    {booking.itinerary?.activities?.map((a: any, i: number) => (
                      <div key={i} className="bg-card-hover rounded-lg p-2 mb-1 text-sm">
                        <div className="font-medium">{a.name}</div>
                        <div className="text-muted">{a.duration}</div>
                        <div className="text-accent">${a.price}</div>
                      </div>
                    )) || <div className="text-muted text-sm">None</div>}
                  </div>
                </div>

                {/* Total & Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-border">
                  <div className="text-xl font-bold">
                    Total: ${booking.total_cost?.toFixed(2) || '0.00'}
                  </div>
                  <div className="flex gap-2">
                    {booking.status === 'confirmed' && (
                      <button
                        onClick={() => handleStatusUpdate(booking.booking_id, 'completed')}
                        className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors"
                      >
                        Mark Completed
                      </button>
                    )}
                    {booking.status !== 'cancelled' && (
                      <button
                        onClick={() => handleStatusUpdate(booking.booking_id, 'cancelled')}
                        className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors"
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
