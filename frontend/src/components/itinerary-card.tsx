'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plane, Hotel, MapPin, Calendar, DollarSign } from 'lucide-react'
import type { Itinerary } from '@/lib/api'

interface ItineraryCardProps {
  itinerary: Itinerary
}

export function ItineraryCard({ itinerary }: ItineraryCardProps) {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin className="h-5 w-5 text-blue-500" />
          {itinerary.destination}
        </CardTitle>
        <CardDescription className="flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          {itinerary.start_date} - {itinerary.end_date}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Flights */}
        {itinerary.flights && itinerary.flights.length > 0 && (
          <div>
            <h4 className="font-semibold flex items-center gap-2 mb-2">
              <Plane className="h-4 w-4" />
              Flights
            </h4>
            <div className="space-y-2">
              {itinerary.flights.map((flight, index) => (
                <div
                  key={flight.id || index}
                  className="text-sm bg-muted p-2 rounded-md"
                >
                  <div className="font-medium">
                    {flight.airline} {flight.flight_number}
                  </div>
                  <div className="text-muted-foreground">
                    {flight.departure_city} → {flight.arrival_city}
                  </div>
                  <div className="text-green-600 font-medium">
                    ${flight.price?.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Hotels */}
        {itinerary.hotels && itinerary.hotels.length > 0 && (
          <div>
            <h4 className="font-semibold flex items-center gap-2 mb-2">
              <Hotel className="h-4 w-4" />
              Accommodations
            </h4>
            <div className="space-y-2">
              {itinerary.hotels.map((hotel, index) => (
                <div
                  key={hotel.id || index}
                  className="text-sm bg-muted p-2 rounded-md"
                >
                  <div className="font-medium">{hotel.name}</div>
                  <div className="text-muted-foreground">
                    Rating: {hotel.rating} ★
                  </div>
                  <div className="text-green-600 font-medium">
                    ${hotel.price_per_night?.toFixed(2)}/night
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Activities */}
        {itinerary.activities && itinerary.activities.length > 0 && (
          <div>
            <h4 className="font-semibold flex items-center gap-2 mb-2">
              <MapPin className="h-4 w-4" />
              Activities
            </h4>
            <div className="space-y-2">
              {itinerary.activities.map((activity, index) => (
                <div
                  key={activity.id || index}
                  className="text-sm bg-muted p-2 rounded-md"
                >
                  <div className="font-medium">{activity.name}</div>
                  <div className="text-muted-foreground">
                    {activity.category} • {activity.duration_hours}h
                  </div>
                  <div className="text-green-600 font-medium">
                    ${activity.price?.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Total */}
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between">
            <span className="font-semibold flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Estimated Total
            </span>
            <span className="text-xl font-bold text-green-600">
              ${itinerary.total_price?.toFixed(2)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
