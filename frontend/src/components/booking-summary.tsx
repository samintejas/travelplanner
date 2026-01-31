'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, CheckCircle } from 'lucide-react'
import { confirmBooking, type Itinerary } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'

interface BookingSummaryProps {
  sessionId: string
  itinerary: Itinerary
  open: boolean
  onClose: () => void
  onConfirm: () => void
}

export function BookingSummary({
  sessionId,
  itinerary,
  open,
  onClose,
  onConfirm,
}: BookingSummaryProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isConfirmed, setIsConfirmed] = useState(false)
  const { toast } = useToast()

  const handleConfirm = async () => {
    if (!name.trim() || !email.trim()) {
      toast({
        title: 'Missing Information',
        description: 'Please provide your name and email.',
        variant: 'destructive',
      })
      return
    }

    setIsLoading(true)
    try {
      await confirmBooking(sessionId, name, email)
      setIsConfirmed(true)
      toast({
        title: 'Booking Confirmed!',
        description: 'Check your email for confirmation details.',
      })
      setTimeout(() => {
        onConfirm()
      }, 2000)
    } catch (error) {
      toast({
        title: 'Booking Failed',
        description: 'There was an error confirming your booking. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (isConfirmed) {
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent>
          <div className="flex flex-col items-center justify-center py-8">
            <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
            <h2 className="text-2xl font-bold mb-2">Booking Confirmed!</h2>
            <p className="text-muted-foreground text-center">
              Your trip to {itinerary.destination} has been booked.
              <br />
              A confirmation email will be sent to {email}.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Confirm Your Booking</DialogTitle>
          <DialogDescription>
            Review your trip details and provide your information to complete the booking.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Trip Summary */}
          <div className="bg-muted p-4 rounded-lg space-y-2">
            <h4 className="font-semibold">{itinerary.destination}</h4>
            <p className="text-sm text-muted-foreground">
              {itinerary.start_date} - {itinerary.end_date}
            </p>
            <p className="text-lg font-bold text-green-600">
              Total: ${itinerary.total_price?.toFixed(2)}
            </p>
          </div>

          {/* User Information */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@example.com"
              />
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              'Confirm Booking'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
