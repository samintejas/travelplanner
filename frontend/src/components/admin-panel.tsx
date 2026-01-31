'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/components/ui/use-toast'
import {
  getBookings,
  adminQuery,
  getNotifications,
  type Booking,
} from '@/lib/api'
import {
  Search,
  Users,
  Bell,
  Calendar,
  MapPin,
  Mail,
  Loader2,
} from 'lucide-react'

interface AdminPanelProps {
  password: string
}

export function AdminPanel({ password }: AdminPanelProps) {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [notifications, setNotifications] = useState<unknown[]>([])
  const [query, setQuery] = useState('')
  const [queryResult, setQueryResult] = useState<{
    answer: string
    sources: string[]
  } | null>(null)
  const [isLoadingBookings, setIsLoadingBookings] = useState(true)
  const [isLoadingQuery, setIsLoadingQuery] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadBookings()
    loadNotifications()
  }, [password])

  const loadBookings = async () => {
    setIsLoadingBookings(true)
    try {
      const data = await getBookings(password)
      setBookings(data.bookings || [])
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load bookings',
        variant: 'destructive',
      })
    } finally {
      setIsLoadingBookings(false)
    }
  }

  const loadNotifications = async () => {
    try {
      const data = await getNotifications(password)
      setNotifications(data.notifications || [])
    } catch (error) {
      console.error('Failed to load notifications:', error)
    }
  }

  const handleQuery = async () => {
    if (!query.trim()) return

    setIsLoadingQuery(true)
    try {
      const result = await adminQuery(query, password)
      setQueryResult(result)
    } catch (error) {
      toast({
        title: 'Query Failed',
        description: 'Failed to execute RAG query',
        variant: 'destructive',
      })
    } finally {
      setIsLoadingQuery(false)
    }
  }

  return (
    <Tabs defaultValue="bookings" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="bookings" className="gap-2">
          <Users className="h-4 w-4" />
          Bookings
        </TabsTrigger>
        <TabsTrigger value="query" className="gap-2">
          <Search className="h-4 w-4" />
          RAG Query
        </TabsTrigger>
        <TabsTrigger value="notifications" className="gap-2">
          <Bell className="h-4 w-4" />
          Notifications
          {notifications.length > 0 && (
            <span className="ml-1 bg-red-500 text-white text-xs rounded-full px-2">
              {notifications.length}
            </span>
          )}
        </TabsTrigger>
      </TabsList>

      {/* Bookings Tab */}
      <TabsContent value="bookings" className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">All Bookings</h2>
          <Button onClick={loadBookings} variant="outline" size="sm">
            Refresh
          </Button>
        </div>

        {isLoadingBookings ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        ) : bookings.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Users className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No bookings yet</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {bookings.map((booking) => (
              <Card key={booking.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <MapPin className="h-5 w-5 text-blue-500" />
                        {booking.itinerary?.destination || 'Unknown Destination'}
                      </CardTitle>
                      <CardDescription>
                        Booking ID: {booking.id.slice(0, 8)}...
                      </CardDescription>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        booking.status === 'confirmed'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {booking.status}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <span>{booking.user_name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="h-4 w-4 text-muted-foreground" />
                        <span>{booking.user_email}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span>
                          {booking.itinerary?.start_date} -{' '}
                          {booking.itinerary?.end_date}
                        </span>
                      </div>
                      <div className="text-sm font-medium text-green-600">
                        Total: ${booking.itinerary?.total_price?.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </TabsContent>

      {/* RAG Query Tab */}
      <TabsContent value="query" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Query Conversations & Bookings</CardTitle>
            <CardDescription>
              Use natural language to search through user conversations and booking data.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., What destinations are most popular?"
                onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
              />
              <Button onClick={handleQuery} disabled={isLoadingQuery}>
                {isLoadingQuery ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>

            {queryResult && (
              <div className="space-y-4 mt-4">
                <div className="bg-muted p-4 rounded-lg">
                  <Label className="text-sm font-medium mb-2 block">
                    Answer
                  </Label>
                  <p className="whitespace-pre-wrap">{queryResult.answer}</p>
                </div>

                {queryResult.sources.length > 0 && (
                  <div>
                    <Label className="text-sm font-medium mb-2 block">
                      Sources
                    </Label>
                    <div className="flex flex-wrap gap-2">
                      {queryResult.sources.map((source, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 bg-secondary rounded text-xs"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      {/* Notifications Tab */}
      <TabsContent value="notifications" className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Notifications</h2>
          <Button onClick={loadNotifications} variant="outline" size="sm">
            Refresh
          </Button>
        </div>

        {notifications.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Bell className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No notifications</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-2">
            {notifications.map((notification: unknown, i) => {
              const notif = notification as {
                type: string
                message: string
                user_name?: string
                destination?: string
              }
              return (
                <Card key={i}>
                  <CardContent className="py-4">
                    <div className="flex items-start gap-3">
                      <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <Bell className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">{notif.message}</p>
                        <p className="text-sm text-muted-foreground">
                          {notif.type}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </TabsContent>
    </Tabs>
  )
}
