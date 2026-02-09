'use client';

import { useState, useEffect } from 'react';
import { MessageSquare, Plus, CheckCircle, Clock } from 'lucide-react';
import { getSessions, type SessionInfo } from '@/lib/api';

interface SessionHistoryProps {
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewSession: () => void;
}

export default function SessionHistory({
  currentSessionId,
  onSelectSession,
  onNewSession,
}: SessionHistoryProps) {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, [currentSessionId]);

  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data.sessions);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
    setLoading(false);
  };

  return (
    <div className="w-64 bg-card border-r border-border flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <button
          onClick={onNewSession}
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

          {loading ? (
            <div className="text-center text-muted py-4 text-sm">Loading...</div>
          ) : sessions.length === 0 ? (
            <div className="text-center text-muted py-4 text-sm">No sessions yet</div>
          ) : (
            <div className="space-y-1">
              {sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => onSelectSession(session.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                    currentSessionId === session.id
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
                      <CheckCircle size={14} className="text-success" />
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
  );
}
