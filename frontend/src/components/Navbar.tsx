'use client';

import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import TierBadge from './TierBadge';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <nav className="navbar">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-2xl">🏀</span>
              <span className="text-xl font-bold" style={{ color: 'var(--accent-green)' }}>NBA Props</span>
            </Link>
            
            <div className="hidden md:flex ml-10 space-x-8">
              <Link href="/dashboard" className="nav-link">
                Dashboard
              </Link>
              <Link href="/props" className="nav-link">
                Props
              </Link>
              <Link href="/education" className="nav-link">
                Education
              </Link>
              <Link href="/pricing" className="nav-link">
                Pricing
              </Link>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <TierBadge 
                  tier={(user?.subscription_tier as 'free' | 'basic' | 'pro') || 'free'} 
                  size="sm" 
                  showIcon={true}
                />
                <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>{user?.email}</div>
                <button
                  onClick={logout}
                  className="nav-link"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="nav-link"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="btn-primary"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
