'use client';

interface TierBadgeProps {
  tier: 'free' | 'basic' | 'pro';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export default function TierBadge({ tier, size = 'md', showIcon = false }: TierBadgeProps) {
  const styles: Record<string, React.CSSProperties> = {
    free: {
      background: 'rgba(255, 255, 255, 0.1)',
      color: '#aaa',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    basic: {
      background: 'linear-gradient(135deg, rgba(0, 255, 127, 0.2), rgba(0, 255, 127, 0.1))',
      color: 'var(--accent-green, #00ff7f)',
      border: '1px solid var(--accent-green, #00ff7f)',
    },
    pro: {
      background: 'linear-gradient(135deg, rgba(128, 0, 255, 0.2), rgba(128, 0, 255, 0.1))',
      color: 'var(--accent-purple, #8000ff)',
      border: '1px solid var(--accent-purple, #8000ff)',
    },
  };

  const sizes: Record<string, React.CSSProperties> = {
    sm: { padding: '0.2rem 0.5rem', fontSize: '0.7rem' },
    md: { padding: '0.35rem 0.75rem', fontSize: '0.8rem' },
    lg: { padding: '0.5rem 1rem', fontSize: '0.95rem' },
  };

  const icons: Record<string, string> = {
    free: '🆓',
    basic: '⭐',
    pro: '👑',
  };

  return (
    <span
      style={{
        ...styles[tier],
        ...sizes[size],
        borderRadius: '6px',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.3rem',
        whiteSpace: 'nowrap',
      }}
    >
      {showIcon && <span>{icons[tier]}</span>}
      {tier}
    </span>
  );
}

// Feature list with check/x marks
interface FeatureListProps {
  features: { name: string; included: boolean }[];
}

export function FeatureList({ features }: FeatureListProps) {
  return (
    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      {features.map((feature, index) => (
        <li
          key={index}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.5rem 0',
            color: feature.included ? '#fff' : '#666',
          }}
        >
          <span
            style={{
              color: feature.included ? 'var(--accent-green, #00ff7f)' : '#666',
              fontSize: '1rem',
            }}
          >
            {feature.included ? '✓' : '✗'}
          </span>
          <span style={{ textDecoration: feature.included ? 'none' : 'line-through' }}>
            {feature.name}
          </span>
        </li>
      ))}
    </ul>
  );
}

// Tier comparison card
interface TierCardProps {
  name: string;
  price: string;
  description: string;
  features: { name: string; included: boolean }[];
  isCurrentTier?: boolean;
  isPopular?: boolean;
  onSelect?: () => void;
}

export function TierCard({
  name,
  price,
  description,
  features,
  isCurrentTier = false,
  isPopular = false,
  onSelect,
}: TierCardProps) {
  const tierColor =
    name.toLowerCase() === 'pro'
      ? 'var(--accent-purple, #8000ff)'
      : 'var(--accent-green, #00ff7f)';

  return (
    <div
      style={{
        background: 'var(--bg-card, #1a1a1a)',
        border: isPopular ? `2px solid ${tierColor}` : '1px solid rgba(255,255,255,0.1)',
        borderRadius: '16px',
        padding: '2rem',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {isPopular && (
        <div
          style={{
            position: 'absolute',
            top: '-12px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: tierColor,
            color: '#000',
            padding: '0.25rem 1rem',
            borderRadius: '12px',
            fontSize: '0.75rem',
            fontWeight: 700,
            textTransform: 'uppercase',
          }}
        >
          Most Popular
        </div>
      )}

      <h3 style={{ color: '#fff', marginBottom: '0.25rem', fontSize: '1.5rem' }}>
        {name}
      </h3>
      <p style={{ color: '#888', marginBottom: '1rem', fontSize: '0.9rem' }}>
        {description}
      </p>

      <div style={{ marginBottom: '1.5rem' }}>
        <span style={{ color: tierColor, fontSize: '2.5rem', fontWeight: 700 }}>
          {price}
        </span>
        <span style={{ color: '#888', fontSize: '0.9rem' }}>/month</span>
      </div>

      <FeatureList features={features} />

      <button
        onClick={onSelect}
        disabled={isCurrentTier}
        style={{
          marginTop: 'auto',
          padding: '0.875rem 1.5rem',
          borderRadius: '8px',
          border: isCurrentTier ? '1px solid rgba(255,255,255,0.2)' : 'none',
          background: isCurrentTier ? 'transparent' : tierColor,
          color: isCurrentTier ? '#888' : '#000',
          fontWeight: 600,
          fontSize: '1rem',
          cursor: isCurrentTier ? 'default' : 'pointer',
          transition: 'transform 0.2s, box-shadow 0.2s',
        }}
      >
        {isCurrentTier ? 'Current Plan' : `Upgrade to ${name}`}
      </button>
    </div>
  );
}
