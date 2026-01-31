'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ChatInterface } from '@/components/chat-interface'
import { generateSessionId } from '@/lib/api'
import { ArrowLeft, Plane } from 'lucide-react'

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string>('')

  useEffect(() => {
    // Generate session ID on client side only
    setSessionId(generateSessionId())
  }, [])

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <Plane className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">Travel Concierge AI</h1>
            </div>
          </div>
          <div className="text-sm text-muted-foreground">
            Session: {sessionId.slice(0, 15)}...
          </div>
        </div>
      </header>

      {/* Chat Interface */}
      <main className="container mx-auto px-4 py-4">
        <ChatInterface sessionId={sessionId} />
      </main>
    </div>
  )
}
