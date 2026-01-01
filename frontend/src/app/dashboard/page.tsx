'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { dataApi, paymentsApi, PlayerCard, Game, Injury } from '@/lib/api';
import PlayerCardComponent from '@/components/PlayerCard';

interface DashboardStats {
  totalCards: number;
  teams: string[];
  propTypes: string[];
  avgScore: number;
  highScoreCount: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, loadUser } = useAuthStore();
  const [topCards, setTopCards] = useState<PlayerCard[]>([]);
  const [todayGames, setTodayGames] = useState<Game[]>([]);
  const [injuries, setInjuries] = useState<Injury[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  // Host mode - no login required for dashboard
  // useEffect(() => {
  //   if (!authLoading && !isAuthenticated) {
  //     router.push('/login');
  //   }
  // }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch all dashboard data in parallel
        const [cardsRes, todayRes, injuriesRes] = await Promise.all([
          dataApi.getTopCards(6),
          dataApi.getTodaysGames(),
          dataApi.getInjuries(),
        ]);

        setTopCards(cardsRes.cards || []);
        setTodayGames(todayRes.games || []);
        setInjuries((injuriesRes.injuries || []).filter((i: Injury) => i.isOut).slice(0, 10));
        
        // Calculate stats from all cards
        const allCardsRes = await dataApi.getCards({ per_page: 500 });
        const allCards = allCardsRes.cards || [];
        const scores = allCards.map((c: PlayerCard) => c.score || 0);
        setStats({
          totalCards: allCardsRes.total || allCards.length,
          teams: Array.from(new Set(allCards.map((c: PlayerCard) => c.team).filter(Boolean))) as string[],
          propTypes: Array.from(new Set(allCards.map((c: PlayerCard) => c.prop).filter(Boolean))) as string[],
          avgScore: scores.length > 0 ? scores.reduce((a: number, b: number) => a + b, 0) / scores.length : 0,
          highScoreCount: scores.filter((s: number) => s >= 80).length,
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    }

    // Host mode - always fetch data
    fetchData();
  }, []);

  const handleUpgrade = async () => {
    try {
      const { checkout_url } = await paymentsApi.createCheckoutSession();
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Error creating checkout session:', error);
    }
  };

  const handleManageSubscription = async () => {
    try {
      const { portal_url } = await paymentsApi.createPortalSession();
      window.location.href = portal_url;
    } catch (error) {
      console.error('Error creating portal session:', error);
    }
  };

  if (isLoading && topCards.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div style={{ color: 'var(--text-secondary)' }}>Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="page-title">
          Welcome back, {user?.full_name || user?.email?.split('@')[0]}!
        </h1>
        <p className="page-subtitle">Here&apos;s your daily prop analysis</p>
      </div>

      {/* Host Mode - Full Access */}

      {/* Stats Overview */}
      <div className="grid md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Props" value={stats?.totalCards.toString() || '0'} />
        <StatCard 
          label="Today's Games" 
          value={todayGames.length.toString()} 
        />
        <StatCard 
          label="High Score Props (80+)" 
          value={stats?.highScoreCount.toString() || '0'} 
          isActive={true}
        />
        <StatCard 
          label="Avg Score" 
          value={stats?.avgScore.toFixed(1) || '0'} 
        />
      </div>

      {/* Today's Games Section */}
      {todayGames.length > 0 && (
        <div className="dashboard-card mb-8">
          <h2 className="dashboard-card-title mb-4">🏀 Today&apos;s Games ({todayGames.length})</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {todayGames.map((game, idx) => (
              <div 
                key={idx} 
                style={{ 
                  background: 'rgba(0,0,0,0.3)', 
                  borderRadius: '8px', 
                  padding: '1rem',
                  border: '1px solid rgba(0, 255, 127, 0.1)'
                }}
              >
                <div className="flex justify-between items-center">
                  <span className="font-semibold">{game.away}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>@</span>
                  <span className="font-semibold">{game.home}</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                  {game.time ? new Date(game.time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : 'TBD'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Injuries */}
      {injuries.length > 0 && (
        <div className="dashboard-card mb-8">
          <h2 className="dashboard-card-title mb-4">🏥 Key Injuries (Out)</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-3">
            {injuries.map((injury, idx) => (
              <div 
                key={idx}
                style={{ 
                  background: 'rgba(255,68,68,0.1)', 
                  borderRadius: '8px',
                  padding: '0.75rem',
                  border: '1px solid rgba(255,68,68,0.2)'
                }}
              >
                <div className="font-semibold" style={{ fontSize: '0.9rem' }}>{injury.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {injury.team} • {injury.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Subscription Management */}
      {user?.subscription_tier !== 'free' && (
        <div className="mb-8">
          <button
            onClick={handleManageSubscription}
            className="form-link"
          >
            Manage Subscription →
          </button>
        </div>
      )}

      {/* Top Props */}
      <div className="mb-8">
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }} className="mb-4">Today&apos;s Top Props</h2>
        {isLoading ? (
          <div style={{ color: 'var(--text-secondary)' }}>Loading props...</div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topCards.map((card, idx) => (
              <PlayerCardComponent 
                key={`${card.name}-${card.prop}-${idx}`} 
                card={card}
                showDetails={true}
              />
            ))}
          </div>
        )}
      </div>

      {/* Host Mode - Full Access */}
    </div>
  );
}

function StatCard({ label, value, isActive = false }: { label: string; value: string; isActive?: boolean }) {
  return (
    <div className="dashboard-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color: isActive ? 'var(--accent-green)' : undefined }}>{value}</div>
    </div>
  );
}
