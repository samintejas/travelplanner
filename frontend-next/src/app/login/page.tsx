'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plane, User, Shield, Mail, UserCircle } from 'lucide-react';
import { useAuth, UserRole } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState<UserRole>('customer');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('Please enter your email');
      return;
    }

    if (!email.includes('@')) {
      setError('Please enter a valid email');
      return;
    }

    login(email, name || email.split('@')[0], role);

    if (role === 'admin') {
      router.push('/admin');
    } else {
      router.push('/chat');
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Plane className="text-accent" size={40} />
          </div>
          <h1 className="text-3xl font-bold">
            Travel<span className="text-accent">Concierge</span>
          </h1>
          <p className="text-muted mt-2">Sign in to plan your perfect trip</p>
        </div>

        {/* Login Form */}
        <div className="bg-card border border-border rounded-2xl p-6">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium mb-3">Sign in as</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setRole('customer')}
                  className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 transition-all ${
                    role === 'customer'
                      ? 'border-accent bg-accent/10 text-white'
                      : 'border-border bg-card-hover text-muted hover:border-accent/50'
                  }`}
                >
                  <User size={20} />
                  <span className="font-medium">Customer</span>
                </button>
                <button
                  type="button"
                  onClick={() => setRole('admin')}
                  className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 transition-all ${
                    role === 'admin'
                      ? 'border-accent bg-accent/10 text-white'
                      : 'border-border bg-card-hover text-muted hover:border-accent/50'
                  }`}
                >
                  <Shield size={20} />
                  <span className="font-medium">Admin</span>
                </button>
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={20} />
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full pl-11 pr-4 py-3 bg-card-hover border border-border rounded-xl focus:outline-none focus:border-accent"
                />
              </div>
            </div>

            {/* Name (Optional) */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2">
                Name <span className="text-muted">(optional)</span>
              </label>
              <div className="relative">
                <UserCircle className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={20} />
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="w-full pl-11 pr-4 py-3 bg-card-hover border border-border rounded-xl focus:outline-none focus:border-accent"
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              className="w-full py-3 bg-accent hover:bg-accent-hover text-white rounded-xl font-medium transition-colors"
            >
              Sign In
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-xs text-muted text-center mb-3">Quick demo access:</p>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => {
                  setEmail('customer@demo.com');
                  setName('Demo Customer');
                  setRole('customer');
                }}
                className="text-xs px-3 py-2 bg-card-hover rounded-lg hover:bg-border transition-colors"
              >
                Customer Demo
              </button>
              <button
                onClick={() => {
                  setEmail('admin@demo.com');
                  setName('Admin User');
                  setRole('admin');
                }}
                className="text-xs px-3 py-2 bg-card-hover rounded-lg hover:bg-border transition-colors"
              >
                Admin Demo
              </button>
            </div>
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-6">
          <a
            href="/"
            className="text-muted hover:text-white text-sm transition-colors"
          >
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
