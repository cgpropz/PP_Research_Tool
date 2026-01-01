'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { dataApi, PlayerCard, GameLog, Injury } from '@/lib/api';
import PlayerCardComponent from '@/components/PlayerCard';

export default function PlayerPage() {
  const params = useParams();
  const playerSlug = params.slug as string;
  const [playerCards, setPlayerCards] = useState<PlayerCard[]>([]);
  const [gamelogs, setGamelogs] = useState<GameLog[]>([]);
  const [injury, setInjury] = useState<Injury | null>(null);
  const [position, setPosition] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPlayer() {
      setIsLoading(true);
      setError(null);
      try {
        // Try to get full player data
        const data = await dataApi.getPlayerBySlug(playerSlug);
        setPlayerCards(data.props || []);
        setGamelogs(data.gamelogs || []);
        setInjury(data.injury);
        setPosition(data.position);
      } catch (err: any) {
        // Fallback to just cards search
        try {
          const searchName = playerSlug.replace(/-/g, ' ');
          const cardsRes = await dataApi.getCards({ player_name: searchName });
          setPlayerCards(cardsRes.cards);
        } catch {
          setError('Player not found');
        }
      } finally {
        setIsLoading(false);
      }
    }

    if (playerSlug) {
      fetchPlayer();
    }
  }, [playerSlug]);

  const playerName = playerCards[0]?.name || playerSlug.replace(/-/g, ' ');
  const team = playerCards[0]?.team;
  const playerId = playerCards[0]?.player_id;
  const playerImageUrl = playerId 
    ? `https://cdn.nba.com/headshots/nba/latest/260x190/${playerId}.png`
    : null;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Back Link */}
      <Link 
        href="/props" 
        className="inline-flex items-center text-[#00ff7f] hover:underline mb-6"
      >
        ← Back to Props
      </Link>

      {isLoading ? (
        <div className="text-center py-12" style={{ color: 'var(--text-secondary)' }}>Loading player data...</div>
      ) : error ? (
        <div className="text-center py-12">
          <div style={{ color: '#ff6b6b', fontSize: '1.25rem' }} className="mb-4">{error}</div>
          <Link href="/props" className="btn-primary">
            Browse All Props
          </Link>
        </div>
      ) : (
        <>
          {/* Player Header */}
          <div className="dashboard-card mb-8">
            <div className="flex flex-col md:flex-row items-center gap-6">
              {playerImageUrl && (
                <img 
                  src={playerImageUrl}
                  alt={playerName}
                  className="w-40 h-32 object-contain"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              )}
              <div className="text-center md:text-left flex-1">
                <h1 style={{ fontSize: '2rem', fontWeight: 700 }} className="text-white mb-2">{playerName}</h1>
                <div className="flex items-center gap-3 justify-center md:justify-start flex-wrap">
                  {team && (
                    <span className={`team-${team} team-badge`}>{team}</span>
                  )}
                  {position && (
                    <span className="prop-type">{position}</span>
                  )}
                  {injury && (
                    <span style={{ 
                      background: injury.isOut ? 'rgba(255,68,68,0.2)' : 'rgba(255,224,102,0.2)',
                      color: injury.isOut ? '#ff6b6b' : '#ffe066',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                    }}>
                      {injury.status}: {injury.detail}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Games */}
          {gamelogs.length > 0 && (
            <div className="dashboard-card mb-8">
              <h2 className="dashboard-card-title mb-4">📊 Last {Math.min(gamelogs.length, 10)} Games</h2>
              <div className="overflow-x-auto">
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(0, 255, 127, 0.2)' }}>
                      <th style={{ textAlign: 'left', padding: '0.5rem', color: 'var(--text-secondary)' }}>Date</th>
                      <th style={{ textAlign: 'left', padding: '0.5rem', color: 'var(--text-secondary)' }}>Matchup</th>
                      <th style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--text-secondary)' }}>MIN</th>
                      <th style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--text-secondary)' }}>PTS</th>
                      <th style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--text-secondary)' }}>REB</th>
                      <th style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--text-secondary)' }}>AST</th>
                      <th style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--text-secondary)' }}>3PM</th>
                      <th style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--text-secondary)' }}>FP</th>
                    </tr>
                  </thead>
                  <tbody>
                    {gamelogs.slice(0, 10).map((log, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '0.5rem', color: 'var(--text-secondary)' }}>{log['GAME DATE']}</td>
                        <td style={{ padding: '0.5rem' }}>
                          {log['MATCH UP']}
                          <span style={{ 
                            marginLeft: '0.5rem',
                            color: log['W/L'] === 'W' ? 'var(--accent-green)' : '#ff6b6b',
                            fontSize: '0.75rem',
                          }}>
                            {log['W/L']}
                          </span>
                        </td>
                        <td style={{ textAlign: 'center', padding: '0.5rem' }}>{log.MIN}</td>
                        <td style={{ textAlign: 'center', padding: '0.5rem', fontWeight: 600 }}>{log.PTS}</td>
                        <td style={{ textAlign: 'center', padding: '0.5rem' }}>{log.REB}</td>
                        <td style={{ textAlign: 'center', padding: '0.5rem' }}>{log.AST}</td>
                        <td style={{ textAlign: 'center', padding: '0.5rem' }}>{log['3PM']}</td>
                        <td style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--accent-green)' }}>{log.FP?.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Player Props */}
          <div className="dashboard-card">
            <h2 className="dashboard-card-title mb-4">
              🏀 Available Props ({playerCards.length})
            </h2>

            {playerCards.length === 0 ? (
              <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>
                No props available for this player today
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {playerCards.map((card, idx) => (
                  <PlayerCardComponent
                    key={`${card.prop}-${idx}`}
                    card={card}
                    showDetails={true}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
