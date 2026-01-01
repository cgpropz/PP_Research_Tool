'use client';

import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { paymentsApi } from '@/lib/api';

export default function PricingPage() {
  const { user, isAuthenticated } = useAuthStore();

  const handleSubscribe = async (tier: 'basic' | 'pro') => {
    if (!isAuthenticated) {
      window.location.href = '/register';
      return;
    }

    try {
      const { checkout_url } = await paymentsApi.createCheckoutSession();
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Error creating checkout session:', error);
    }
  };

  return (
    <div className="page-container" style={{ paddingTop: '4rem', paddingBottom: '4rem' }}>
      <div className="text-center mb-16">
        <h1 className="page-title" style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Choose Your Plan</h1>
        <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)' }}>
          Start free, upgrade when you&apos;re ready for more
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {/* Free Tier */}
        <div className="pricing-card">
          <div className="mb-6">
            <h2 className="pricing-name">Free</h2>
            <p style={{ color: 'var(--text-secondary)' }}>Perfect for getting started</p>
          </div>
          
          <div className="mb-6">
            <span className="pricing-price">$0</span>
            <span className="pricing-period">/month</span>
          </div>

          <ul className="space-y-3 mb-8">
            <Feature text="Top 10 props daily" />
            <Feature text="Basic hit rate analysis" />
            <Feature text="Team & prop filters" />
            <Feature text="Mobile responsive" />
            <FeatureDisabled text="Full projections" />
            <FeatureDisabled text="Odds comparison" />
            <FeatureDisabled text="DVP analysis" />
            <FeatureDisabled text="API access" />
          </ul>

          {user?.subscription_tier === 'free' ? (
            <div className="text-center py-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.1)', color: 'var(--text-secondary)' }}>
              Current Plan
            </div>
          ) : (
            <Link
              href="/register"
              className="btn-secondary block text-center"
            >
              Get Started
            </Link>
          )}
        </div>

        {/* Basic Tier */}
        <div className="pricing-card featured">          
          <div className="mb-6">
            <h2 className="pricing-name">Basic</h2>
            <p style={{ color: 'var(--text-secondary)' }}>For serious bettors</p>
          </div>
          
          <div className="mb-6">
            <span className="pricing-price">$9.99</span>
            <span className="pricing-period">/month</span>
          </div>

          <ul className="space-y-3 mb-8">
            <Feature text="All player props" />
            <Feature text="Full hit rate analysis" />
            <Feature text="Smart projections" />
            <Feature text="Odds comparison" />
            <Feature text="Player search" />
            <Feature text="Last 10 game trends" />
            <FeatureDisabled text="DVP analysis" />
            <FeatureDisabled text="API access" />
          </ul>

          {user?.subscription_tier === 'basic' ? (
            <div className="text-center py-3 rounded-lg" style={{ background: 'rgba(0, 255, 127, 0.3)', color: '#fff' }}>
              Current Plan
            </div>
          ) : (
            <button
              onClick={() => handleSubscribe('basic')}
              className="btn-primary"
              style={{ width: '100%', padding: '0.75rem' }}
            >
              {isAuthenticated ? 'Upgrade to Basic' : 'Get Started'}
            </button>
          )}
        </div>

        {/* Pro Tier */}
        <div className="pricing-card">
          <div className="mb-6">
            <h2 className="pricing-name">Pro</h2>
            <p style={{ color: 'var(--text-secondary)' }}>Maximum edge</p>
          </div>
          
          <div className="mb-6">
            <span className="pricing-price" style={{ color: 'var(--accent-purple)' }}>$19.99</span>
            <span className="pricing-period">/month</span>
          </div>

          <ul className="space-y-3 mb-8">
            <Feature text="Everything in Basic" />
            <Feature text="DVP matchup analysis" />
            <Feature text="Advanced projections" />
            <Feature text="API access" />
            <Feature text="Priority support" />
            <Feature text="Early access features" />
            <Feature text="Custom alerts" />
            <Feature text="Export data" />
          </ul>

          {user?.subscription_tier === 'pro' ? (
            <div className="text-center py-3 rounded-lg" style={{ background: 'rgba(128, 0, 255, 0.3)', color: '#fff' }}>
              Current Plan
            </div>
          ) : (
            <button
              onClick={() => handleSubscribe('pro')}
              className="btn-primary"
              style={{ width: '100%', padding: '0.75rem', background: 'linear-gradient(135deg, var(--accent-purple) 0%, #a64dff 100%)' }}
            >
              {isAuthenticated ? 'Upgrade to Pro' : 'Get Started'}
            </button>
          )}
        </div>
      </div>

      {/* FAQ */}
      <div className="mt-20 max-w-3xl mx-auto">
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }} className="text-center mb-8">Frequently Asked Questions</h2>
        
        <div className="space-y-4">
          <FAQItem 
            question="Can I cancel anytime?"
            answer="Yes! You can cancel your subscription at any time. You'll continue to have access until the end of your billing period."
          />
          <FAQItem 
            question="What payment methods do you accept?"
            answer="We accept all major credit cards (Visa, Mastercard, American Express) through our secure payment processor, Stripe."
          />
          <FAQItem 
            question="How often is the data updated?"
            answer="Our prop data is updated multiple times per day to reflect the latest odds, injury news, and game schedules."
          />
          <FAQItem 
            question="Do you offer refunds?"
            answer="We offer a 7-day money-back guarantee. If you're not satisfied, contact support for a full refund."
          />
        </div>
      </div>
    </div>
  );
}

function Feature({ text }: { text: string }) {
  return (
    <li className="pricing-feature">
      <span style={{ color: 'var(--accent-green)' }}>✓</span>
      {text}
    </li>
  );
}

function FeatureDisabled({ text }: { text: string }) {
  return (
    <li className="pricing-feature" style={{ opacity: 0.5 }}>
      <span>✗</span>
      {text}
    </li>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  return (
    <div className="dashboard-card">
      <h3 style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{question}</h3>
      <p style={{ color: 'var(--text-secondary)' }}>{answer}</p>
    </div>
  );
}
