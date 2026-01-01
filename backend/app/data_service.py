"""
NBA Props Data Service
Loads and serves all JSON data files with caching and auto-refresh
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

# Base path for data files (parent of backend)
BASE_PATH = Path(__file__).parent.parent.parent

class DataService:
    """Service to load and cache all NBA Props data files"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_times: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes
        self._lock = threading.Lock()
    
    def _get_file_path(self, filename: str) -> Path:
        """Get full path for a data file"""
        return BASE_PATH / filename
    
    def _load_json(self, filename: str) -> Any:
        """Load a JSON file from disk"""
        path = self._get_file_path(filename)
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[DataService] Error loading {filename}: {e}")
            return None
    
    def _get_cached(self, key: str, filename: str) -> Any:
        """Get data from cache or load from disk"""
        with self._lock:
            now = datetime.now()
            if key in self._cache:
                cache_time = self._cache_times.get(key)
                if cache_time and (now - cache_time) < self._cache_ttl:
                    return self._cache[key]
            
            # Load from disk
            data = self._load_json(filename)
            if data is not None:
                self._cache[key] = data
                self._cache_times[key] = now
            return data
    
    def clear_cache(self, key: Optional[str] = None):
        """Clear cache for a specific key or all"""
        with self._lock:
            if key:
                self._cache.pop(key, None)
                self._cache_times.pop(key, None)
            else:
                self._cache.clear()
                self._cache_times.clear()
    
    # ── Player Cards (main props data) ────────────────────────────────────
    
    def get_player_cards(self) -> List[Dict]:
        """Get all player prop cards"""
        data = self._get_cached('player_cards', 'PLAYER_UI_CARDS_PERFECT.json')
        return data if isinstance(data, list) else []
    
    def get_player_cards_with_dvp(self) -> List[Dict]:
        """Get player cards with DVP data"""
        data = self._get_cached('player_cards_dvp', 'PLAYER_UI_CARDS_WITH_DVP.json')
        return data if isinstance(data, list) else []
    
    # ── DVP (Defense vs Position) ─────────────────────────────────────────
    
    def get_dvp_weighted(self) -> Dict:
        """Get weighted DVP data by position and team"""
        data = self._get_cached('dvp_weighted', 'DVP_2025_weighted.json')
        return data if isinstance(data, dict) else {}
    
    def get_dvp_raw(self) -> Dict:
        """Get raw DVP data"""
        data = self._get_cached('dvp_raw', 'DVP_2025.json')
        return data if isinstance(data, dict) else {}
    
    def get_dvp_latest(self) -> Dict:
        """Get latest DVP data"""
        data = self._get_cached('dvp_latest', 'nba_dvp_latest.json')
        return data if isinstance(data, dict) else {}
    
    # ── Gamelogs ──────────────────────────────────────────────────────────
    
    def get_gamelogs(self) -> List[Dict]:
        """Get all player gamelogs"""
        data = self._get_cached('gamelogs', 'Player_Gamelogs25.json')
        return data if isinstance(data, list) else []
    
    def get_player_gamelogs(self, player_name: str, limit: int = 20) -> List[Dict]:
        """Get gamelogs for a specific player"""
        all_logs = self.get_gamelogs()
        player_logs = [g for g in all_logs if g.get('PLAYER', '').lower() == player_name.lower()]
        # Sort by date descending
        player_logs.sort(key=lambda x: x.get('GAME DATE', ''), reverse=True)
        return player_logs[:limit]
    
    # ── Schedule ──────────────────────────────────────────────────────────
    
    def get_schedule(self) -> List[Dict]:
        """Get NBA schedule"""
        data = self._get_cached('schedule', 'nba_schedule.json')
        return data if isinstance(data, list) else []
    
    def get_todays_games(self) -> List[Dict]:
        """Get today's games"""
        today = datetime.now().strftime('%Y-%m-%d')
        schedule = self.get_schedule()
        return [g for g in schedule if g.get('date') == today]
    
    # ── Injuries ──────────────────────────────────────────────────────────
    
    def get_injuries(self) -> List[Dict]:
        """Get current injury report"""
        data = self._get_cached('injuries', 'nba_injuries.json')
        return data if isinstance(data, list) else []
    
    def get_team_injuries(self, team: str) -> List[Dict]:
        """Get injuries for a specific team"""
        injuries = self.get_injuries()
        return [i for i in injuries if i.get('team', '').upper() == team.upper()]
    
    # ── Odds ──────────────────────────────────────────────────────────────
    
    def get_odds_latest(self) -> Dict:
        """Get latest odds data"""
        data = self._get_cached('odds_latest', 'ODDS_LATEST.json')
        return data if isinstance(data, dict) else {}
    
    def get_player_odds(self) -> Dict:
        """Get player-specific odds"""
        data = self._get_cached('player_odds', 'nba_player_odds.json')
        return data if isinstance(data, dict) else {}
    
    # ── Players ───────────────────────────────────────────────────────────
    
    def get_players(self) -> List[Dict]:
        """Get all NBA players"""
        data = self._get_cached('players', 'players.json')
        return data if isinstance(data, list) else []
    
    def get_player_positions(self) -> Dict:
        """Get player positions mapping"""
        data = self._get_cached('positions', 'nba_players_2025_26_positions.json')
        return data if isinstance(data, dict) else {}
    
    def get_player_by_name(self, name: str) -> Optional[Dict]:
        """Find a player by name"""
        players = self.get_players()
        name_lower = name.lower().strip()
        for p in players:
            full_name = p.get('full_name', '') or p.get('name', '')
            if full_name.lower().strip() == name_lower:
                return p
        return None
    
    # ── Props Lines (raw) ─────────────────────────────────────────────────
    
    def get_props_lines(self) -> List[Dict]:
        """Get raw props lines"""
        data = self._get_cached('props_lines', 'NBA_PURE_STANDARD_SINGLE.json')
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if 'lines' in data:
                return data['lines']
            if 'data' in data:
                return data['data']
        return []
    
    # ── Aggregated Data ───────────────────────────────────────────────────
    
    def get_full_player_data(self, player_name: str) -> Dict:
        """Get comprehensive data for a single player"""
        # Find player
        player = self.get_player_by_name(player_name)
        
        # Get position
        positions = self.get_player_positions()
        position = positions.get(player_name, 'Unknown')
        
        # Get gamelogs
        gamelogs = self.get_player_gamelogs(player_name, limit=20)
        
        # Get all props for this player
        all_cards = self.get_player_cards()
        player_props = [c for c in all_cards if c.get('name', '').lower() == player_name.lower()]
        
        # Get injury status
        injuries = self.get_injuries()
        injury_status = None
        for inj in injuries:
            if inj.get('name', '').lower() == player_name.lower():
                injury_status = inj
                break
        
        return {
            'player': player,
            'position': position,
            'gamelogs': gamelogs,
            'props': player_props,
            'injury': injury_status,
        }
    
    def get_dashboard_data(self) -> Dict:
        """Get aggregated data for dashboard"""
        cards = self.get_player_cards()
        schedule = self.get_todays_games()
        injuries = self.get_injuries()
        
        # Sort cards by score descending
        sorted_cards = sorted(cards, key=lambda x: x.get('score', 0) or 0, reverse=True)
        
        return {
            'top_props': sorted_cards[:20],
            'total_props': len(cards),
            'todays_games': schedule,
            'injury_count': len([i for i in injuries if i.get('isOut', False)]),
            'generated_at': datetime.now().isoformat(),
        }
    
    def get_data_status(self) -> Dict:
        """Get status of all data files"""
        files = {
            'player_cards': 'PLAYER_UI_CARDS_PERFECT.json',
            'gamelogs': 'Player_Gamelogs25.json',
            'dvp': 'DVP_2025_weighted.json',
            'schedule': 'nba_schedule.json',
            'injuries': 'nba_injuries.json',
            'odds': 'ODDS_LATEST.json',
            'players': 'players.json',
            'positions': 'nba_players_2025_26_positions.json',
            'props_lines': 'NBA_PURE_STANDARD_SINGLE.json',
        }
        
        status = {}
        for key, filename in files.items():
            path = self._get_file_path(filename)
            if path.exists():
                stat = path.stat()
                status[key] = {
                    'exists': True,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            else:
                status[key] = {'exists': False}
        
        return status


# Global singleton instance
data_service = DataService()
