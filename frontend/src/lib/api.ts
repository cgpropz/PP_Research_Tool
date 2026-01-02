import axios from 'axios';
import Cookies from 'js-cookie';

// Production Railway URL - hardcoded for reliability
const PRODUCTION_API_URL = 'https://ppresearchtool-production.up.railway.app';
const DEV_API_URL = 'http://localhost:8000';

// Determine if we're in production (browser and not localhost)
const isProduction = typeof window !== 'undefined' && 
  !window.location.hostname.includes('localhost') && 
  !window.location.hostname.includes('127.0.0.1');

// Always use production URL in production, localhost for dev
const API_URL = isProduction ? PRODUCTION_API_URL : DEV_API_URL;

console.log('[API] Using URL:', API_URL, 'isProduction:', isProduction);

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,  // Don't send cookies cross-origin
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = Cookies.get('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      Cookies.remove('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ Auth API ============

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  subscription_tier: 'free' | 'basic' | 'pro';
  subscription_status: string | null;
  subscription_end_date: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  register: async (email: string, password: string, fullName?: string): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  refresh: async (): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/refresh');
    return response.data;
  },
};

// ============ Props API ============

export interface PlayerCard {
  name: string;
  team: string;
  opponent: string;
  prop: string;
  line: number;
  last_5: string;
  last_5_pct: number;
  last_10: string;
  last_10_pct: number;
  last_20: string;
  last_20_pct: number;
  season: string;
  season_pct: number;
  avg: number;
  games: number;
  last_10_values: number[];
  projection: number;
  expected_minutes: number;
  player_id: number;
  score: number;
  spread: number;
  dvp_rank?: number;
  position?: string;
}

export interface PlayerCardsResponse {
  cards: PlayerCard[];
  total: number;
  page: number;
  per_page: number;
}

export const propsApi = {
  getCards: async (params?: {
    page?: number;
    per_page?: number;
    team?: string;
    prop?: string;
    min_score?: number;
    player_name?: string;
  }): Promise<PlayerCardsResponse> => {
    const response = await api.get('/api/props/cards', { params });
    return response.data;
  },

  getTopCards: async (limit?: number, prop?: string): Promise<PlayerCard[]> => {
    const response = await api.get('/api/props/cards/top', {
      params: { limit, prop },
    });
    return response.data;
  },

  getPlayerProps: async (playerName: string): Promise<PlayerCard[]> => {
    const response = await api.get(`/api/props/cards/player/${playerName}`);
    return response.data;
  },

  getOdds: async (playerName?: string, team?: string) => {
    const response = await api.get('/api/props/odds', {
      params: { player_name: playerName, team },
    });
    return response.data;
  },

  getDvp: async (team?: string) => {
    const response = await api.get('/api/props/dvp', { params: { team } });
    return response.data;
  },

  getTeams: async (): Promise<{ teams: string[] }> => {
    const response = await api.get('/api/data/teams');
    return response.data;
  },

  getPropTypes: async (): Promise<{ props: string[] }> => {
    const response = await api.get('/api/data/prop-types');
    return response.data;
  },
};

// ============ Data API (New) ============

export interface GameLog {
  PLAYER: string;
  TEAM: string;
  'MATCH UP': string;
  'GAME DATE': string;
  'W/L': string;
  MIN: number;
  PTS: number;
  REB: number;
  AST: number;
  STL: number;
  BLK: number;
  TOV: number;
  FP: number;
  '3PM': number;
  'FG%': number | null;
}

export interface Injury {
  name: string;
  team: string;
  position: string;
  status: string;
  detail: string;
  isOut: boolean;
}

export interface Game {
  id: string;
  home: string;
  away: string;
  date: string;
  time: string;
}

export interface PlayerData {
  player: {
    id: number;
    full_name: string;
  } | null;
  position: string;
  gamelogs: GameLog[];
  props: PlayerCard[];
  injury: Injury | null;
}

export interface DashboardData {
  top_props: PlayerCard[];
  total_props: number;
  todays_games: Game[];
  injury_count: number;
  generated_at: string;
}

export const dataApi = {
  // Cards
  getCards: async (params?: {
    page?: number;
    per_page?: number;
    team?: string;
    prop?: string;
    player_name?: string;
    min_score?: number;
    min_minutes?: number;
    hit_rate?: string;
    matchup?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<PlayerCardsResponse & { pages: number }> => {
    const response = await api.get('/api/data/cards', { params });
    return response.data;
  },

  getTopCards: async (limit: number = 20): Promise<{ cards: PlayerCard[]; total: number }> => {
    const response = await api.get('/api/data/cards/top', { params: { limit } });
    return response.data;
  },

  getPlayerCards: async (playerName: string): Promise<{ cards: PlayerCard[]; total: number }> => {
    const response = await api.get(`/api/data/cards/player/${encodeURIComponent(playerName)}`);
    return response.data;
  },

  // DVP
  getDvp: async (): Promise<Record<string, Record<string, Record<string, { score: number; rank: number }>>>> => {
    const response = await api.get('/api/data/dvp');
    return response.data;
  },

  getDvpByPosition: async (position: string) => {
    const response = await api.get(`/api/data/dvp/${position}`);
    return response.data;
  },

  getDvpByPositionTeam: async (position: string, team: string) => {
    const response = await api.get(`/api/data/dvp/${position}/${team}`);
    return response.data;
  },

  // Gamelogs
  getGamelogs: async (params?: { player?: string; team?: string; limit?: number }) => {
    const response = await api.get('/api/data/gamelogs', { params });
    return response.data;
  },

  getPlayerGamelogs: async (playerName: string, limit: number = 20): Promise<{ gamelogs: GameLog[]; total: number }> => {
    const response = await api.get(`/api/data/gamelogs/${encodeURIComponent(playerName)}`, { params: { limit } });
    return response.data;
  },

  // Schedule
  getSchedule: async (params?: { team?: string; date?: string }): Promise<{ games: Game[]; total: number }> => {
    const response = await api.get('/api/data/schedule', { params });
    return response.data;
  },

  getTodaysGames: async (): Promise<{ games: Game[]; total: number }> => {
    const response = await api.get('/api/data/schedule/today');
    return response.data;
  },

  // Injuries
  getInjuries: async (params?: { team?: string; status?: string }): Promise<{ injuries: Injury[]; total: number }> => {
    const response = await api.get('/api/data/injuries', { params });
    return response.data;
  },

  getTeamInjuries: async (team: string): Promise<{ injuries: Injury[]; total: number }> => {
    const response = await api.get(`/api/data/injuries/${team}`);
    return response.data;
  },

  // Odds
  getOdds: async () => {
    const response = await api.get('/api/data/odds');
    return response.data;
  },

  getOddsEvents: async () => {
    const response = await api.get('/api/data/odds/events');
    return response.data;
  },

  // Players
  getPlayers: async (params?: { search?: string; limit?: number }) => {
    const response = await api.get('/api/data/players', { params });
    return response.data;
  },

  getPlayerPositions: async (): Promise<Record<string, string>> => {
    const response = await api.get('/api/data/players/positions');
    return response.data;
  },

  getPlayerFullData: async (playerName: string): Promise<PlayerData> => {
    const response = await api.get(`/api/data/players/${encodeURIComponent(playerName)}`);
    return response.data;
  },

  getPlayerBySlug: async (slug: string): Promise<PlayerData> => {
    const response = await api.get(`/api/data/players/slug/${slug}`);
    return response.data;
  },

  // Dashboard
  getDashboard: async (): Promise<DashboardData> => {
    const response = await api.get('/api/data/dashboard');
    return response.data;
  },

  // Status
  getDataStatus: async () => {
    const response = await api.get('/api/data/status');
    return response.data;
  },

  refreshCache: async (key?: string) => {
    const response = await api.post('/api/data/refresh', null, { params: { key } });
    return response.data;
  },
};

// ============ Payments API ============

export const paymentsApi = {
  createCheckoutSession: async (): Promise<{ checkout_url: string; session_id: string }> => {
    const response = await api.post('/api/payments/create-checkout-session');
    return response.data;
  },

  createPortalSession: async (): Promise<{ portal_url: string }> => {
    const response = await api.post('/api/payments/create-portal-session');
    return response.data;
  },

  getSubscription: async () => {
    const response = await api.get('/api/payments/subscription');
    return response.data;
  },
};

export default api;
