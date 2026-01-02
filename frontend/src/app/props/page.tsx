'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import { dataApi, PlayerCard, Game } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import PlayerCardComponent from '@/components/PlayerCard';

// Sort options matching props-trend.html
const SORT_OPTIONS = [
  { value: 'score-desc', label: 'Best Score🔥' },
  { value: 'score-asc', label: 'Worst Score' },
  { value: 'projection-desc', label: 'Highest Projection' },
  { value: 'projection-asc', label: 'Lowest Projection' },
  { value: 'line-desc', label: 'Highest Line' },
  { value: 'line-asc', label: 'Lowest Line' },
  { value: 'minutes-desc', label: 'Most Minutes' },
  { value: 'minutes-asc', label: 'Fewest Minutes' },
  { value: 'last_10_pct-desc', label: 'Best Hit Rate' },
];

const HIT_RATE_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: '80', label: '80%+' },
  { value: '70', label: '70%+' },
  { value: '60', label: '60%+' },
  { value: '40', label: '40%+' },
  { value: 'miss', label: 'Misses Only' },
];

export default function PropsPage() {
  const { user } = useAuthStore();
  const [allCards, setAllCards] = useState<PlayerCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [teams, setTeams] = useState<string[]>([]);
  const [propTypes, setPropTypes] = useState<string[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [minMinutes, setMinMinutes] = useState<number>(30);  // Default to 30 minutes
  const [selectedProp, setSelectedProp] = useState<string>('');
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [sortOption, setSortOption] = useState<string>('score-desc');
  const [selectedMatchup, setSelectedMatchup] = useState<string>('all');
  const [hitRate, setHitRate] = useState<string>('all');
  const [page, setPage] = useState(1);
  const perPage = 24;

  // Fetch all data on mount
  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      try {
        // Fetch all cards and schedule in parallel
        const [cardsResponse, scheduleResponse] = await Promise.all([
          dataApi.getCards({ per_page: 500 }),
          dataApi.getSchedule(),
        ]);
        
        const cards = cardsResponse.cards || [];
        setAllCards(cards);
        
        // Extract unique teams and prop types
        const uniqueTeams = Array.from(new Set(cards.map((c: PlayerCard) => c.team).filter(Boolean))) as string[];
        const uniqueProps = Array.from(new Set(cards.map((c: PlayerCard) => c.prop).filter(Boolean))) as string[];
        setTeams(uniqueTeams.sort());
        setPropTypes(uniqueProps.sort());
        setGames(scheduleResponse.games || []);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  // Group games by date for the matchup dropdown
  const gamesByDate = useMemo(() => {
    const grouped: Record<string, Game[]> = {};
    games.forEach(game => {
      if (!grouped[game.date]) grouped[game.date] = [];
      grouped[game.date].push(game);
    });
    return grouped;
  }, [games]);

  // Filter cards based on selections
  const filteredCards = useMemo(() => {
    let result = [...allCards];
    
    // Min minutes filter
    if (minMinutes > 0) {
      result = result.filter(c => (c.expected_minutes || 0) >= minMinutes);
    }
    
    // Prop type filter
    if (selectedProp) {
      result = result.filter(c => c.prop === selectedProp);
    }
    
    // Team filter
    if (selectedTeam) {
      result = result.filter(c => c.team === selectedTeam);
    }
    
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(c => c.name?.toLowerCase().includes(query));
    }
    
    // Hit rate filter
    if (hitRate !== 'all') {
      if (hitRate === 'miss') {
        result = result.filter(c => (c.last_10_pct || 0) < 50);
      } else {
        const threshold = parseFloat(hitRate);
        result = result.filter(c => (c.last_10_pct || 0) >= threshold);
      }
    }
    
    // Matchup filter
    if (selectedMatchup !== 'all') {
      if (selectedMatchup.startsWith('date:')) {
        const dateStr = selectedMatchup.replace('date:', '');
        const gamesOnDate = gamesByDate[dateStr] || [];
        const teamsPlaying = new Set<string>();
        gamesOnDate.forEach(g => {
          teamsPlaying.add(g.home);
          teamsPlaying.add(g.away);
        });
        result = result.filter(c => teamsPlaying.has(c.team) || teamsPlaying.has(c.opponent));
      } else {
        // Specific game id
        const game = games.find(g => g.id === selectedMatchup);
        if (game) {
          result = result.filter(c => c.team === game.home || c.team === game.away);
        }
      }
    }
    
    // Sort
    const [sortBy, sortOrder] = sortOption.split('-');
    const isDesc = sortOrder === 'desc';
    
    result.sort((a, b) => {
      let aVal: number = 0, bVal: number = 0;
      
      switch (sortBy) {
        case 'score':
          aVal = a.score || 0;
          bVal = b.score || 0;
          break;
        case 'projection':
          aVal = a.projection || 0;
          bVal = b.projection || 0;
          break;
        case 'line':
          aVal = a.line || 0;
          bVal = b.line || 0;
          break;
        case 'minutes':
          aVal = a.expected_minutes || 0;
          bVal = b.expected_minutes || 0;
          break;
        case 'last_10_pct':
          aVal = a.last_10_pct || 0;
          bVal = b.last_10_pct || 0;
          break;
      }
      
      return isDesc ? bVal - aVal : aVal - bVal;
    });
    
    return result;
  }, [allCards, minMinutes, selectedProp, selectedTeam, searchQuery, hitRate, selectedMatchup, sortOption, gamesByDate, games]);

  // Paginated cards
  const paginatedCards = useMemo(() => {
    const start = (page - 1) * perPage;
    return filteredCards.slice(start, start + perPage);
  }, [filteredCards, page]);

  const totalPages = Math.ceil(filteredCards.length / perPage);

  const clearFilters = useCallback(() => {
    setSearchQuery('');
    setMinMinutes(30);
    setSelectedProp('');
    setSelectedTeam('');
    setSortOption('score-desc');
    setSelectedMatchup('all');
    setHitRate('all');
    setPage(1);
  }, []);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [searchQuery, minMinutes, selectedProp, selectedTeam, sortOption, selectedMatchup, hitRate]);

  return (
    <div className="page-container">
      <h1 className="page-title mb-6">NBA PrizePicks Edge🏀🔥</h1>

      {/* Filters Row - Matching props-trend.html style */}
      <div className="dashboard-card mb-8">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 items-end">
          {/* Search */}
          <div className="col-span-2 lg:col-span-1">
            <label className="filter-label">Search player</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search player..."
              className="filter-input"
            />
          </div>

          {/* Min Minutes */}
          <div>
            <label className="filter-label">Min Minutes</label>
            <input
              type="number"
              value={minMinutes}
              onChange={(e) => setMinMinutes(Number(e.target.value) || 0)}
              min={0}
              max={48}
              className="filter-input"
            />
          </div>

          {/* Prop Type Filter */}
          <div>
            <label className="filter-label">Prop Type</label>
            <select
              value={selectedProp}
              onChange={(e) => setSelectedProp(e.target.value)}
              className="filter-select"
            >
              <option value="">All Props</option>
              {propTypes.map((prop) => (
                <option key={prop} value={prop}>{prop}</option>
              ))}
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="filter-label">Sort By</label>
            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value)}
              className="filter-select"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Matchup Filter */}
          <div>
            <label className="filter-label">Game</label>
            <select
              value={selectedMatchup}
              onChange={(e) => setSelectedMatchup(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Games</option>
              {Object.entries(gamesByDate).sort().map(([date, dateGames]) => {
                const dateLabel = new Date(date + 'T00:00:00').toLocaleDateString(undefined, {
                  weekday: 'short',
                  month: 'short',
                  day: 'numeric'
                });
                return (
                  <optgroup key={date} label={dateLabel}>
                    <option value={`date:${date}`}>All Games on {dateLabel}</option>
                    {dateGames.map((game) => (
                      <option key={game.id} value={game.id}>
                        {game.away} @ {game.home}
                      </option>
                    ))}
                  </optgroup>
                );
              })}
            </select>
          </div>

          {/* Hit Rate Filter */}
          <div>
            <label className="filter-label">Hit Rate</label>
            <select
              value={hitRate}
              onChange={(e) => setHitRate(e.target.value)}
              className="filter-select"
            >
              {HIT_RATE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Clear Filters */}
          <div>
            <button
              onClick={clearFilters}
              className="btn-secondary w-full"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="flex justify-between items-center mb-4">
        <p style={{ color: 'var(--text-secondary)' }}>
          Showing {paginatedCards.length} of {filteredCards.length} props
        </p>
        {selectedTeam && (
          <span className="text-sm" style={{ color: 'var(--accent-green)' }}>
            Filtered by: {selectedTeam}
          </span>
        )}
      </div>

      {/* Cards Grid */}
      {isLoading ? (
        <div className="text-center py-12" style={{ color: 'var(--text-secondary)' }}>Loading props...</div>
      ) : paginatedCards.length === 0 ? (
        <div className="text-center py-12" style={{ color: 'var(--text-secondary)' }}>
          No props found. Try adjusting your filters.
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {paginatedCards.map((card, idx) => (
            <PlayerCardComponent
              key={`${card.name}-${card.prop}-${idx}`}
              card={card}
              showDetails={true}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2 mt-8">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary"
            style={{ opacity: page === 1 ? 0.5 : 1 }}
          >
            Previous
          </button>
          <span className="px-4 py-2" style={{ color: 'var(--text-secondary)' }}>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= totalPages}
            className="btn-secondary"
            style={{ opacity: page >= totalPages ? 0.5 : 1 }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
