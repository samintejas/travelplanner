'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Plane, MapPin, Globe, Star, ArrowRight } from 'lucide-react';
import { useAuth } from '@/lib/auth';

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/chat');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
        <div className="text-xl font-semibold">
          Travel<span className="text-accent">Concierge</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="/login"
            className="px-4 py-2 text-muted hover:text-white transition-colors"
          >
            Sign In
          </a>
          <a
            href="/login"
            className="px-5 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg font-medium transition-colors"
          >
            Get Started
          </a>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent/10 border border-accent/20 rounded-full text-accent text-sm mb-6">
            <Star size={16} />
            AI-Powered Travel Planning
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Plan Your Perfect Trip<br />
            <span className="text-accent">Anywhere in the World</span>
          </h1>
          <p className="text-xl text-muted max-w-2xl mx-auto mb-8">
            Your personal AI travel assistant helps you discover flights, hotels, and activities.
            Just tell us where you want to go, and we'll handle the rest.
          </p>
          <a
            href="/login"
            className="inline-flex items-center gap-2 px-8 py-4 bg-accent hover:bg-accent-hover text-white rounded-xl font-semibold text-lg transition-all hover:scale-105"
          >
            Start Planning
            <ArrowRight size={20} />
          </a>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          <div className="bg-card border border-border rounded-2xl p-6 text-center">
            <div className="w-14 h-14 bg-blue-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Plane className="text-blue-500" size={28} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Find Flights</h3>
            <p className="text-muted text-sm">
              Compare flight options and prices from multiple airlines to any destination.
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-6 text-center">
            <div className="w-14 h-14 bg-purple-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <MapPin className="text-purple-500" size={28} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Book Hotels</h3>
            <p className="text-muted text-sm">
              Discover the perfect accommodations that match your style and budget.
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-6 text-center">
            <div className="w-14 h-14 bg-green-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Globe className="text-green-500" size={28} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Plan Activities</h3>
            <p className="text-muted text-sm">
              Get personalized activity recommendations and local experiences.
            </p>
          </div>
        </div>

        {/* How it works */}
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-8">How It Works</h2>
          <div className="flex flex-col md:flex-row items-center justify-center gap-8">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center font-bold">1</div>
              <span>Sign up for free</span>
            </div>
            <div className="hidden md:block text-muted">→</div>
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center font-bold">2</div>
              <span>Tell us your dream trip</span>
            </div>
            <div className="hidden md:block text-muted">→</div>
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center font-bold">3</div>
              <span>Book with one click</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border py-8 text-center text-muted text-sm">
        <p>© 2025 TravelConcierge. AI-powered travel planning.</p>
      </footer>
    </div>
  );
}
