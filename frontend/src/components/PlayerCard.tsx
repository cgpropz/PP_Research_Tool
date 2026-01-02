'use client';

import Link from 'next/link';
import { PlayerCard } from '@/lib/api';

interface Props {
  card: PlayerCard;
  showDetails?: boolean;
}

// NBA team colors
const TEAM_COLORS: Record<string, { bg: string; text: string }> = {
  ATL: { bg: '#E03A3E', text: '#fff' },
  BOS: { bg: '#007A33', text: '#fff' },
  BKN: { bg: '#000000', text: '#fff' },
  CHA: { bg: '#1D1160', text: '#fff' },
  CHI: { bg: '#CE1141', text: '#fff' },
  CLE: { bg: '#6F263D', text: '#fff' },
  DAL: { bg: '#00538C', text: '#fff' },
  DEN: { bg: '#0E2240', text: '#fff' },
  DET: { bg: '#C8102E', text: '#fff' },
  GSW: { bg: '#1D428A', text: '#FFC72C' },
  HOU: { bg: '#CE1141', text: '#fff' },
  IND: { bg: '#002D62', text: '#FDBB30' },
  LAC: { bg: '#C8102E', text: '#fff' },
  LAL: { bg: '#552583', text: '#FDB927' },
  MEM: { bg: '#5D76A9', text: '#fff' },
  MIA: { bg: '#98002E', text: '#fff' },
  MIL: { bg: '#00471B', text: '#fff' },
  MIN: { bg: '#0C2340', text: '#fff' },
  NOP: { bg: '#0C2340', text: '#fff' },
  NYK: { bg: '#006BB6', text: '#fff' },
  OKC: { bg: '#007AC1', text: '#fff' },
  ORL: { bg: '#0077C0', text: '#fff' },
  PHI: { bg: '#006BB6', text: '#fff' },
  PHX: { bg: '#1D1160', text: '#fff' },
  POR: { bg: '#E03A3E', text: '#fff' },
  SAC: { bg: '#5A2D81', text: '#fff' },
  SAS: { bg: '#C4CED4', text: '#000' },
  TOR: { bg: '#CE1141', text: '#fff' },
  UTA: { bg: '#002B5C', text: '#fff' },
  WAS: { bg: '#002B5C', text: '#fff' },
};

// Color scale for score (30=red, 50=yellow, 70=green)
function getScoreColor(score: number): string {
  if (score <= 30) return '#ff2d2d';
  if (score >= 70) return '#1aff00';
  if (score < 50) {
    // Red to Yellow: 30-50
    const percent = (score - 30) / 20;
    const r = 255;
    const g = Math.round(45 + percent * 179);
    const b = Math.round(45 + percent * 57);
    return `rgb(${r},${g},${b})`;
  } else {
    // Yellow to Green: 50-70
    const percent = (score - 50) / 20;
    const r = Math.round(255 - percent * 229);
    const g = Math.round(224 + percent * 31);
    const b = Math.round(102 - percent * 102);
    return `rgb(${r},${g},${b})`;
  }
}

// Color scale for spread (good spread = positive/green, bad = negative/red)
function getSpreadColor(spread: number): { bg: string; text: string } {
  const abs = Math.abs(spread);
  if (spread > 0) {
    // Favorite (positive spread for opponent - easier matchup)
    if (abs >= 7) return { bg: '#1aff00', text: '#181f1b' };
    if (abs >= 5) return { bg: '#66ff99', text: '#181f1b' };
    if (abs >= 3) return { bg: '#99ffbb', text: '#181f1b' };
    return { bg: '#222b22', text: '#fff' };
  } else {
    // Underdog (negative spread)
    if (abs >= 7) return { bg: '#ff2d2d', text: '#fff' };
    if (abs >= 5) return { bg: '#ffe066', text: '#181f1b' };
    if (abs >= 3) return { bg: '#ffee99', text: '#181f1b' };
    return { bg: '#222b22', text: '#fff' };
  }
}

// Color scale for DVP rank (1 = hardest = red, 30 = easiest = green)
function getDvpColor(rank: number): string {
  if (rank <= 1) return '#ff2d2d';
  if (rank >= 30) return '#1aff00';
  if (rank < 15) {
    // Red to Yellow: 1-15 (hard matchups)
    const percent = (rank - 1) / 14;
    const r = 255;
    const g = Math.round(45 + percent * 179);
    const b = Math.round(45 + percent * 57);
    return `rgb(${r},${g},${b})`;
  } else {
    // Yellow to Green: 15-30 (easier matchups)
    const percent = (rank - 15) / 15;
    const r = Math.round(255 - percent * 229);
    const g = Math.round(224 + percent * 31);
    const b = Math.round(102 - percent * 102);
    return `rgb(${r},${g},${b})`;
  }
}

function getHitRateColor(pct: number): string {
  if (pct >= 80) return '#00ff7f';
  if (pct >= 60) return '#66ff99';
  if (pct >= 40) return '#ffe066';
  return '#ff4444';
}

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export default function PlayerCardComponent({ card, showDetails = true }: Props) {
  const teamColor = TEAM_COLORS[card.team] || { bg: '#222', text: '#fff' };
  const oppColor = card.opponent ? (TEAM_COLORS[card.opponent] || { bg: '#444', text: '#fff' }) : null;
  const playerSlug = slugify(card.name);
  const playerImageUrl = card.player_id 
    ? `https://cdn.nba.com/headshots/nba/latest/260x190/${card.player_id}.png`
    : null;

  // Get spread colors
  const spreadStyle = card.spread ? getSpreadColor(card.spread) : null;
  
  // Get DVP color
  const dvpColor = card.dvp_rank ? getDvpColor(card.dvp_rank) : '#ffe066';

  return (
    <div className="player-card p-5">
      {/* Minutes Badge */}
      {card.expected_minutes && (
        <div className="minutes-badge">
          {card.expected_minutes.toFixed(1)} min
        </div>
      )}

      {/* Spread Badge with Color Scale */}
      {card.spread !== undefined && card.spread !== null && (
        <div 
          className="spreads-badge"
          style={{ 
            background: spreadStyle?.bg || '#222b22', 
            color: spreadStyle?.text || '#fff',
            boxShadow: '0 0 10px 2px #00ff7f44'
          }}
        >
          {card.spread > 0 ? '+' : ''}{card.spread} spread
        </div>
      )}

      {/* Player Image */}
      {playerImageUrl && (
        <div className="flex justify-center mb-3 mt-8">
          <img 
            src={playerImageUrl} 
            alt={card.name}
            className="w-32 h-24 object-contain"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        </div>
      )}

      {/* Player Name - Clickable */}
      <Link 
        href={`/player/${playerSlug}`} 
        className="player-name player-link block mb-2"
      >
        {card.name}
      </Link>

      {/* Team Badges */}
      <div className="flex justify-center gap-2 mb-3 flex-wrap">
        {card.position && (
          <span 
            className="position-badge" 
            style={{ background: '#8000ff', color: '#fff' }}
          >
            {card.position}
          </span>
        )}
        <span 
          className="team-badge" 
          style={{ background: teamColor.bg, color: teamColor.text }}
        >
          {card.team}
        </span>
        {card.opponent && oppColor && (
          <span 
            className="opp-badge" 
            style={{ background: oppColor.bg, color: oppColor.text }}
          >
            vs {card.opponent}
          </span>
        )}
      </div>

      {/* Prop Type */}
      <div className="prop-type mb-4">
        {card.prop}
      </div>

      {/* Line, Projection, Score, DVP */}
      <div className="flex justify-between gap-2 mb-4 flex-wrap">
        <div className="prop-block flex-1 min-w-[70px]">
          <span className="prop-label">LINE</span>
          <span className="prop-value">{card.line}</span>
        </div>
        {showDetails && card.projection && (
          <div className="prop-block flex-1 min-w-[70px]">
            <span className="prop-label">PROJECTION</span>
            <span 
              className="prop-value"
              style={{ color: card.projection > card.line ? '#00ff7f' : '#ff4444' }}
            >
              {card.projection.toFixed(1)}
            </span>
          </div>
        )}
        {card.score !== undefined && (
          <div className="prop-block flex-1 min-w-[70px]">
            <span className="prop-label">SCORE</span>
            <span 
              className="prop-value"
              style={{ color: getScoreColor(card.score) }}
            >
              {card.score.toFixed(1)}
            </span>
          </div>
        )}
        {card.dvp_rank !== undefined && card.dvp_rank !== null && (
          <div className="prop-block flex-1 min-w-[70px]">
            <span className="prop-label">DVP</span>
            <span 
              className="prop-value"
              style={{ color: dvpColor }}
            >
              {card.dvp_rank}
            </span>
          </div>
        )}
      </div>

      {/* Hit Rate Panel */}
      <div className="hitrate-panel">
        {/* Progress Bars */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {[
            { label: 'L5', value: card.last_5_pct, record: card.last_5 },
            { label: 'L10', value: card.last_10_pct, record: card.last_10 },
            { label: 'Full', value: card.season_pct, record: card.season },
          ].map((item) => (
            <div key={item.label} className="flex flex-col items-center">
              <span className="progress-label">{item.label}</span>
              <span 
                className="progress-value text-lg font-bold"
                style={{ color: getHitRateColor(item.value ?? 0) }}
              >
                {item.value?.toFixed(0) || 0}%
              </span>
            </div>
          ))}
        </div>

        {/* Last 10 Games Bar Chart */}
        {showDetails && card.last_10_values && card.last_10_values.length > 0 && (
          <div className="mt-4">
            <div className="bars-container justify-center" style={{ height: '80px' }}>
              {card.last_10_values.map((value, idx) => {
                const max = Math.max(...(card.last_10_values || []), card.line);
                const height = (value / max) * 100;
                const isOver = value > card.line;
                return (
                  <div 
                    key={idx}
                    className="flex flex-col items-center"
                    style={{ flex: 1, minWidth: '20px', maxWidth: '30px' }}
                  >
                    <div
                      className="bar relative"
                      style={{ 
                        height: `${Math.max(height, 10)}%`,
                        width: '100%',
                        background: isOver ? '#1aff00' : '#ff2d2d',
                        borderRadius: '4px 4px 0 0',
                      }}
                    >
                      <span 
                        className="absolute -top-5 left-1/2 -translate-x-1/2 text-xs font-bold"
                        style={{ color: isOver ? '#1aff00' : '#ff4444' }}
                      >
                        {value}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between mt-1">
              {card.last_10_values.map((_, idx) => (
                <span 
                  key={idx}
                  className="text-xs text-gray-500"
                  style={{ flex: 1, minWidth: '20px', maxWidth: '30px', textAlign: 'center' }}
                >
                  G{idx + 1}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Click to view more */}
      <Link 
        href={`/player/${playerSlug}`}
        className="block text-center mt-4 text-sm text-[#00ff7f] hover:underline"
      >
        View Player Details →
      </Link>
    </div>
  );
}
