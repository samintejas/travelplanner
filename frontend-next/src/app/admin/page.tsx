'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Plane, Hotel, MapPin, CheckCircle, XCircle, Clock, LogOut, MessageSquare, RefreshCw } from 'lucide-react';
import { getBookings, updateBookingStatus, getSessions, type Booking, type SessionInfo } from '@/lib/api';
import { useAuth } from '@/lib/auth';

type TabType = 'bookings' | 'sessions';

export default function AdminPage() {
  const { user, role, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('bookings');
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    confirmed: 0,
    completed: 0,
    revenue: 0,
  });

  // Redirect non-admin users
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    } else if (role !== 'admin') {
      router.push('/chat');
    }
  }, [isAuthenticated, role, router]);

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

  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data.sessions);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  useEffect(() => {
    fetchBookings();
    fetchSessions();
    const interval = setInterval(() => {
      fetchBookings();
      fetchSessions();
    }, 5000);
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

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Don't render if not admin
  if (!isAuthenticated || role !== 'admin') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-muted">Checking access...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
        <div className="text-xl font-semibold">
          Travel<span className="text-accent">Concierge</span>{' '}
          <span className="text-muted font-normal">Admin</span>
        </div>
        <div className="flex items-center gap-4">
          <nav className="flex gap-4">
            <a href="/chat" className="text-muted hover:text-white transition-colors">
              Chat
            </a>
            <a href="/admin" className="text-white">
              Admin
            </a>
          </nav>
          {isAuthenticated && (
            <div className="flex items-center gap-3 ml-4 pl-4 border-l border-border">
              <span className="text-sm text-muted">
                {user?.name || user?.email}
                {role === 'admin' && (
                  <span className="ml-2 px-2 py-0.5 bg-accent/20 text-accent text-xs rounded-full">
                    Admin
                  </span>
                )}
              </span>
              <button
                onClick={handleLogout}
                className="p-2 text-muted hover:text-white transition-colors"
                title="Logout"
              >
                <LogOut size={18} />
              </button>
            </div>
          )}
          {!isAuthenticated && (
            <a
              href="/login"
              className="ml-4 px-4 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg text-sm font-medium transition-colors"
            >
              Sign In
            </a>
          )}
        </div>
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

        {/* Tabs */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('bookings')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'bookings'
                  ? 'bg-accent text-white'
                  : 'bg-card-hover text-muted hover:text-white'
              }`}
            >
              Confirmed Bookings
            </button>
            <button
              onClick={() => setActiveTab('sessions')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'sessions'
                  ? 'bg-accent text-white'
                  : 'bg-card-hover text-muted hover:text-white'
              }`}
            >
              All Sessions
            </button>
          </div>
          <button
            onClick={() => { fetchBookings(); fetchSessions(); }}
            className="p-2 text-muted hover:text-white transition-colors"
            title="Refresh"
          >
            <RefreshCw size={18} />
          </button>
        </div>

        {/* Bookings Tab */}
        {activeTab === 'bookings' && (
          <>
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
                        className={`px-3 py-1 rounded-full text-sm font-medium flex items-center ${getStatusColor(
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
          </>
        )}

        {/* Sessions Tab */}
        {activeTab === 'sessions' && (
          <>
            {sessions.length === 0 ? (
              <div className="text-center text-muted py-12 bg-card border border-border rounded-xl">
                No sessions yet
              </div>
            ) : (
              <div className="bg-card border border-border rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left px-4 py-3 text-muted text-sm font-medium">Session ID</th>
                      <th className="text-left px-4 py-3 text-muted text-sm font-medium">Created</th>
                      <th className="text-left px-4 py-3 text-muted text-sm font-medium">Destination</th>
                      <th className="text-center px-4 py-3 text-muted text-sm font-medium">Messages</th>
                      <th className="text-center px-4 py-3 text-muted text-sm font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.map((session) => (
                      <tr key={session.id} className="border-b border-border hover:bg-card-hover">
                        <td className="px-4 py-3 font-mono text-sm">{session.id.slice(0, 8)}...</td>
                        <td className="px-4 py-3 text-sm text-muted">
                          {new Date(session.created_at).toLocaleString()}
                        </td>
                        <td className="px-4 py-3">
                          {session.destination || <span className="text-muted">Not set</span>}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className="inline-flex items-center gap-1 text-sm">
                            <MessageSquare size={14} className="text-muted" />
                            {session.message_count}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          {session.confirmed ? (
                            <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded-full text-xs font-medium">
                              Booked
                            </span>
                          ) : (
                            <span className="px-2 py-1 bg-yellow-500/20 text-yellow-500 rounded-full text-xs font-medium">
                              In Progress
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
