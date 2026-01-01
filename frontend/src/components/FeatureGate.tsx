'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { useFeatures, FeatureAccess, getRequiredTier } from '@/lib/useFeatures';

interface FeatureGateProps {
  feature: keyof FeatureAccess;
  children: ReactNode;
  fallback?: ReactNode;
  showUpgrade?: boolean;
  blurContent?: boolean;
}

export default function FeatureGate({
  feature,
  children,
  fallback,
  showUpgrade = true,
  blurContent = true,
}: FeatureGateProps) {
  const features = useFeatures();
  const hasAccess = features[feature] as boolean;
  const requiredTier = getRequiredTier(feature);

  if (hasAccess) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (!showUpgrade) {
    return null;
  }

  return (
    <div className="feature-gate-container" style={{ position: 'relative' }}>
      <div
        style={{
          filter: blurContent ? 'blur(4px)' : 'none',
          opacity: 0.4,
          pointerEvents: 'none',
          userSelect: 'none',
        }}
      >
        {children}
      </div>
      <div
        className="feature-gate-overlay"
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.85)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '12px',
          padding: '2rem',
          textAlign: 'center',
          zIndex: 10,
        }}
      >
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔒</div>
        <h3
          style={{
            color: '#fff',
            marginBottom: '0.5rem',
            fontSize: '1.5rem',
            fontWeight: 700,
          }}
        >
          {requiredTier === 'pro' ? 'Pro Feature' : 'Premium Feature'}
        </h3>
        <p
          style={{
            color: 'var(--text-secondary, #888)',
            marginBottom: '1.5rem',
            maxWidth: '300px',
          }}
        >
          Upgrade to {requiredTier === 'pro' ? 'Pro' : 'Basic'} to unlock this
          feature and get the edge you need
        </p>
        <Link
          href="/pricing"
          style={{
            background: 'var(--accent-green, #00ff7f)',
            color: '#000',
            padding: '0.75rem 2rem',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '1rem',
            textDecoration: 'none',
            transition: 'transform 0.2s, box-shadow 0.2s',
          }}
        >
          View Pricing
        </Link>
      </div>
    </div>
  );
}

// Inline feature check component for conditional rendering
interface FeatureCheckProps {
  feature: keyof FeatureAccess;
  children: ReactNode;
}

export function FeatureCheck({ feature, children }: FeatureCheckProps) {
  const features = useFeatures();
  const hasAccess = features[feature] as boolean;

  if (!hasAccess) return null;
  return <>{children}</>;
}

// Upgrade prompt banner
interface UpgradeBannerProps {
  currentTier: string;
  targetTier?: 'basic' | 'pro';
  message?: string;
}

export function UpgradeBanner({
  currentTier,
  targetTier = 'basic',
  message,
}: UpgradeBannerProps) {
  if (currentTier !== 'free' && targetTier === 'basic') return null;
  if (currentTier === 'pro') return null;

  const defaultMessage =
    currentTier === 'free'
      ? "You're on the Free tier - limited to top 10 props"
      : 'Upgrade to Pro for DVP analysis and advanced features';

  return (
    <div
      className="upgrade-banner"
      style={{
        background:
          targetTier === 'pro'
            ? 'rgba(128, 0, 255, 0.1)'
            : 'rgba(255, 255, 127, 0.1)',
        border: `1px solid ${targetTier === 'pro' ? 'rgba(128, 0, 255, 0.3)' : 'rgba(255, 255, 127, 0.3)'}`,
        borderRadius: '12px',
        padding: '1rem 1.5rem',
        marginBottom: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
      }}
    >
      <p
        style={{
          color: targetTier === 'pro' ? '#a855f7' : '#ffe066',
          margin: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}
      >
        <span>📢</span> {message || defaultMessage}
      </p>
      <Link
        href="/pricing"
        style={{
          color: 'var(--accent-green, #00ff7f)',
          textDecoration: 'none',
          fontWeight: 600,
          fontSize: '0.9rem',
        }}
      >
        Upgrade to {targetTier === 'pro' ? 'Pro' : 'Basic'} →
      </Link>
    </div>
  );
}
