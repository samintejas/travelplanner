import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plane, Hotel, MapPin, MessageSquare } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Travel Concierge AI
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Your intelligent travel companion. Plan your perfect trip with our AI-powered assistant
          that handles everything from flights to activities.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/chat">
            <Button size="lg" className="gap-2">
              <MessageSquare className="h-5 w-5" />
              Start Planning
            </Button>
          </Link>
          <Link href="/admin">
            <Button size="lg" variant="outline">
              Admin Dashboard
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <MessageSquare className="h-6 w-6 text-blue-600" />
              </div>
              <CardTitle>Chat with AI</CardTitle>
              <CardDescription>
                Tell us about your dream vacation - destination, dates, interests, and budget.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Our AI understands your preferences and asks smart follow-up questions
                to create the perfect itinerary.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <MapPin className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle>Get Personalized Plans</CardTitle>
              <CardDescription>
                Receive a custom itinerary with flights, hotels, and activities.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                We search through thousands of options to find the best matches
                for your style and budget.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Plane className="h-6 w-6 text-purple-600" />
              </div>
              <CardTitle>Book with Confidence</CardTitle>
              <CardDescription>
                Confirm your booking and get ready for your adventure.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Review your complete itinerary and confirm with just a click.
                We handle the rest!
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Popular Destinations */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          Popular Destinations
        </h2>
        <div className="grid md:grid-cols-4 gap-6">
          {['Paris', 'London', 'Tokyo', 'Rome'].map((city) => (
            <Card key={city} className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow">
              <div className="h-40 bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                <Hotel className="h-16 w-16 text-white opacity-50" />
              </div>
              <CardHeader>
                <CardTitle>{city}</CardTitle>
                <CardDescription>
                  Explore the wonders of {city}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-20">
        <div className="container mx-auto px-4 text-center">
          <h3 className="text-2xl font-bold mb-4">Travel Concierge AI</h3>
          <p className="text-gray-400 mb-8">
            Making travel planning effortless with AI
          </p>
          <div className="flex justify-center gap-8">
            <Link href="/chat" className="hover:text-blue-400 transition-colors">
              Start Planning
            </Link>
            <Link href="/admin" className="hover:text-blue-400 transition-colors">
              Admin
            </Link>
          </div>
        </div>
      </footer>
    </main>
  )
}
