'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);
  
  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="homepage">
      {/* Animated Background Orbs */}
      <div className="hero-orb hero-orb-1" />
      <div className="hero-orb hero-orb-2" />
      <div className="hero-orb hero-orb-3" />
      
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className={`hero-badge ${isVisible ? 'animate-in' : ''}`}>
            <span className="hero-badge-dot" />
            <span>Live data updated every 5 minutes</span>
          </div>
          
          <h1 className={`hero-title ${isVisible ? 'animate-in delay-1' : ''}`}>
            <span className="hero-title-gradient">Make Smarter Bets.</span>
            <br />
            <span className="hero-title-white">Beat the Books.</span>
          </h1>
          
          <p className={`hero-subtitle ${isVisible ? 'animate-in delay-2' : ''}`}>
            Advanced NBA player prop analysis with hit rates, projections, 
            and real-time odds comparison. All in one place.
          </p>
          
          <div className={`hero-cta ${isVisible ? 'animate-in delay-3' : ''}`}>
            <Link href="/props" className="hero-btn-primary">
              <span>Find your next bet</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4.166 10h11.667M10 4.167L15.833 10 10 15.833" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
            <Link href="/register" className="hero-btn-secondary">
              Create Free Account
            </Link>
          </div>
          
          {/* Trust Badges */}
          <div className={`trust-badges ${isVisible ? 'animate-in delay-4' : ''}`}>
            <div className="trust-badge">
              <span className="trust-number">451+</span>
              <span className="trust-label">Daily Props</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-badge">
              <span className="trust-number">5</span>
              <span className="trust-label">Sportsbooks</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-badge">
              <span className="trust-number">30+</span>
              <span className="trust-label">Teams Covered</span>
            </div>
          </div>
        </div>
        
        {/* Floating Product Preview */}
        <div className={`hero-preview ${isVisible ? 'animate-in delay-2' : ''}`}>
          <div className="preview-card">
            <div className="preview-header">
              <div className="preview-live-dot" />
              <span>Live Props</span>
            </div>
            <div className="preview-player">
              <div className="preview-player-img">
                <img 
                  src="https://cdn.nba.com/headshots/nba/latest/260x190/203507.png" 
                  alt="Player"
                  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                />
              </div>
              <div className="preview-player-info">
                <span className="preview-player-name">Giannis Antetokounmpo</span>
                <span className="preview-player-team">MIL vs BOS</span>
              </div>
            </div>
            <div className="preview-prop">
              <span className="preview-prop-type">Points + Rebounds + Assists</span>
              <div className="preview-prop-line">
                <span className="preview-line-value">Over 51.5</span>
                <span className="preview-line-hit">L10: 80%</span>
              </div>
            </div>
            <div className="preview-stats">
              <div className="preview-stat">
                <span className="preview-stat-label">Projection</span>
                <span className="preview-stat-value good">54.2</span>
              </div>
              <div className="preview-stat">
                <span className="preview-stat-label">DVP</span>
                <span className="preview-stat-value neutral">12</span>
              </div>
              <div className="preview-stat">
                <span className="preview-stat-label">Score</span>
                <span className="preview-stat-value excellent">78.5</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-header">
          <h2 className="section-title">
            Everything you need to <span className="text-gradient">win</span>
          </h2>
          <p className="section-subtitle">
            Powerful tools designed for serious bettors
          </p>
        </div>
        
        <div className="features-grid">
          {[
            {
              icon: '📊',
              title: 'Hit Rate Analysis',
              description: 'Track L5, L10, L20 and full season performance to find consistent trends.',
              stat: '90%',
              statLabel: 'Accuracy'
            },
            {
              icon: '🎯',
              title: 'Smart Projections',
              description: 'Data-driven projections based on matchups, pace, and historical data.',
              stat: '450+',
              statLabel: 'Daily Picks'
            },
            {
              icon: '⚡',
              title: 'Real-Time Odds',
              description: 'Compare lines across FanDuel, DraftKings, and all major sportsbooks.',
              stat: '5min',
              statLabel: 'Updates'
            },
            {
              icon: '🏆',
              title: 'DVP Matchups',
              description: 'Defense vs Position analysis to exploit weak defenses.',
              stat: '30',
              statLabel: 'Teams'
            }
          ].map((feature, idx) => (
            <div 
              key={idx} 
              className={`feature-card ${activeFeature === idx ? 'feature-card-active' : ''}`}
              onMouseEnter={() => setActiveFeature(idx)}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <div className="feature-stat">
                <span className="feature-stat-value">{feature.stat}</span>
                <span className="feature-stat-label">{feature.statLabel}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="how-section">
        <div className="how-header">
          <h2 className="section-title">
            How it <span className="text-gradient">works</span>
          </h2>
        </div>
        
        <div className="how-steps">
          {[
            { step: '01', title: 'Browse Props', desc: 'Explore hundreds of player props with advanced filtering' },
            { step: '02', title: 'Analyze Data', desc: 'Check hit rates, projections, and DVP matchups' },
            { step: '03', title: 'Compare Odds', desc: 'Find the best lines across all major sportsbooks' },
            { step: '04', title: 'Place Bets', desc: 'Execute your picks with confidence' },
          ].map((item, idx) => (
            <div key={idx} className="how-step">
              <div className="how-step-number">{item.step}</div>
              <div className="how-step-content">
                <h3 className="how-step-title">{item.title}</h3>
                <p className="how-step-desc">{item.desc}</p>
              </div>
              {idx < 3 && <div className="how-step-connector" />}
            </div>
          ))}
        </div>
      </section>

      {/* Stats Banner */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-number">10K+</span>
            <span className="stat-label">Props Analyzed</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">5</span>
            <span className="stat-label">Sportsbooks</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">24/7</span>
            <span className="stat-label">Live Updates</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">Free</span>
            <span className="stat-label">To Start</span>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section">
        <div className="pricing-header">
          <h2 className="section-title">
            Simple, transparent <span className="text-gradient">pricing</span>
          </h2>
          <p className="section-subtitle">Start free. Upgrade when you&apos;re ready.</p>
        </div>
        
        <div className="pricing-cards">
          <div className="pricing-card-new">
            <div className="pricing-card-header">
              <span className="pricing-tier">Starter</span>
              <div className="pricing-amount">
                <span className="pricing-currency">$</span>
                <span className="pricing-value">0</span>
              </div>
              <span className="pricing-period">Forever free</span>
            </div>
            <ul className="pricing-features">
              <li><span className="check">✓</span> Top 10 daily props</li>
              <li><span className="check">✓</span> Basic hit rates</li>
              <li><span className="check">✓</span> Team filters</li>
              <li><span className="check">✓</span> Mobile friendly</li>
            </ul>
            <Link href="/register" className="pricing-cta secondary">
              Get Started
            </Link>
          </div>
          
          <div className="pricing-card-new featured">
            <div className="pricing-popular">Most Popular</div>
            <div className="pricing-card-header">
              <span className="pricing-tier">Pro</span>
              <div className="pricing-amount">
                <span className="pricing-currency">$</span>
                <span className="pricing-value">19</span>
                <span className="pricing-decimal">.99</span>
              </div>
              <span className="pricing-period">per month</span>
            </div>
            <ul className="pricing-features">
              <li><span className="check">✓</span> <strong>All player props</strong></li>
              <li><span className="check">✓</span> Full projections & DVP</li>
              <li><span className="check">✓</span> Odds comparison</li>
              <li><span className="check">✓</span> Advanced filters</li>
              <li><span className="check">✓</span> API access</li>
              <li><span className="check">✓</span> Priority support</li>
            </ul>
            <Link href="/register" className="pricing-cta primary">
              Start Pro Trial
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to start winning?</h2>
          <p className="cta-subtitle">
            Join thousands of bettors making smarter decisions with data.
          </p>
          <div className="cta-buttons">
            <Link href="/props" className="hero-btn-primary">
              <span>Browse Props Now</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4.166 10h11.667M10 4.167L15.833 10 10 15.833" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="site-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="footer-logo">🏀 NBA Props</span>
            <p className="footer-tagline">Make smarter bets with data.</p>
          </div>
          <div className="footer-links">
            <Link href="/props">Props</Link>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/pricing">Pricing</Link>
          </div>
          <div className="footer-legal">
            <p>© 2026 NBA Props. For entertainment purposes only.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
