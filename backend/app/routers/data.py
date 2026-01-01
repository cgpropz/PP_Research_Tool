"""
NBA Props Data API Endpoints
Serves all data from JSON files with filtering and pagination
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
import re
import unicodedata

from ..data_service import data_service

router = APIRouter(prefix="/data", tags=["data"])


def normalize_name(n: str) -> str:
    """Normalize unicode characters in names"""
    nf = unicodedata.normalize('NFKD', n)
    return ''.join(c for c in nf if not unicodedata.combining(c))


def make_slug(name: str) -> str:
    """Convert player name to URL slug"""
    base = normalize_name(name.lower())
    return re.sub(r'[^a-z0-9]+', '-', base).strip('-')


# ── Status & Health ───────────────────────────────────────────────────────

@router.get("/status")
async def get_data_status():
    """Get status of all data files"""
    return data_service.get_data_status()


@router.post("/refresh")
async def refresh_cache(key: Optional[str] = None):
    """Clear cache to force reload from disk"""
    data_service.clear_cache(key)
    return {"message": f"Cache cleared for: {key or 'all'}"}


# ── Player Cards (Main Props) ─────────────────────────────────────────────

@router.get("/cards")
async def get_cards(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
    team: Optional[str] = None,
    prop: Optional[str] = None,
    player_name: Optional[str] = None,
    min_score: Optional[float] = None,
    min_minutes: Optional[float] = None,
    hit_rate: Optional[str] = None,  # "80", "70", "60", "40", "miss", or "all"
    matchup: Optional[str] = None,  # game id or "date:YYYY-MM-DD"
    sort_by: str = Query("score", regex="^(score|name|team|line|last_10_pct|projection|minutes)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """Get player prop cards with filtering and pagination"""
    cards = data_service.get_player_cards()
    schedule = data_service.get_schedule()
    dvp_data = data_service.get_dvp_weighted()
    positions_data = data_service.get_player_positions()
    
    # Enrich cards with positions from positions file
    for card in cards:
        if not card.get('position'):
            player_name_key = card.get('name', '')
            card['position'] = positions_data.get(player_name_key, '')
    
    # Apply filters
    if team:
        cards = [c for c in cards if c.get('team', '').upper() == team.upper()]
    if prop:
        cards = [c for c in cards if prop.lower() in c.get('prop', '').lower()]
    if player_name:
        cards = [c for c in cards if player_name.lower() in c.get('name', '').lower()]
    if min_score is not None:
        cards = [c for c in cards if (c.get('score') or 0) >= min_score]
    
    # New: Min minutes filter
    if min_minutes is not None:
        cards = [c for c in cards if (c.get('expected_minutes') or 0) >= min_minutes]
    
    # New: Hit rate filter (uses last_10_pct)
    if hit_rate and hit_rate != "all":
        if hit_rate == "miss":
            cards = [c for c in cards if (c.get('last_10_pct') or 0) < 50]
        else:
            try:
                threshold = float(hit_rate)
                cards = [c for c in cards if (c.get('last_10_pct') or 0) >= threshold]
            except ValueError:
                pass
    
    # New: Matchup filter
    if matchup and matchup != "all":
        if matchup.startswith("date:"):
            # Filter by date
            date_str = matchup.replace("date:", "")
            game_teams = set()
            for g in schedule:
                if g.get('date') == date_str:
                    game_teams.add(g.get('home', '').upper())
                    game_teams.add(g.get('away', '').upper())
            cards = [c for c in cards if c.get('team', '').upper() in game_teams or 
                    c.get('opponent', '').upper() in game_teams]
        else:
            # Filter by specific game id
            game = next((g for g in schedule if g.get('id') == matchup), None)
            if game:
                game_teams = {game.get('home', '').upper(), game.get('away', '').upper()}
                cards = [c for c in cards if c.get('team', '').upper() in game_teams]
    
    # Enrich cards with DVP rank
    for card in cards:
        position = card.get('position', '')
        opponent = card.get('opponent', '')
        prop_type = card.get('prop', '')
        
        # Map position to DVP position
        dvp_position = None
        if position in ['PG', 'SG', 'G']:
            dvp_position = 'PG'
        elif position in ['PF', 'SF', 'F']:
            dvp_position = 'SF'
        elif position == 'C':
            dvp_position = 'C'
        
        # Map prop to DVP stat key
        stat_map = {
            'Points': 'pts', 'Rebounds': 'reb', 'Assists': 'ast', 'Steals': 'stl', 
            'Blocks': 'blk', 'Fantasy Score': 'fd', 'Pts+Rebs+Asts': 'pra',
            'Pts+Rebs': 'pr', 'Pts+Asts': 'pa', 'Rebs+Asts': 'ra', '3PM': '3pm',
            'Turnovers': 'to', 'PTS': 'pts', 'REB': 'reb', 'AST': 'ast',
            'Offensive Rebounds': 'oreb', 'Defensive Rebounds': 'dreb'
        }
        stat_key = stat_map.get(prop_type, 'pts')
        
        # Get DVP rank
        dvp_rank = None
        if dvp_position and opponent and dvp_data:
            pos_data = dvp_data.get(dvp_position, {})
            team_data = pos_data.get(opponent, {})
            stat_data = team_data.get(stat_key, {})
            dvp_rank = stat_data.get('rank')
        
        card['dvp_rank'] = dvp_rank
    
    # Sort
    reverse = sort_order == "desc"
    if sort_by == "name":
        cards.sort(key=lambda x: x.get('name', '').lower(), reverse=reverse)
    elif sort_by == "team":
        cards.sort(key=lambda x: x.get('team', ''), reverse=reverse)
    elif sort_by == "line":
        cards.sort(key=lambda x: x.get('line', 0) or 0, reverse=reverse)
    elif sort_by == "last_10_pct":
        cards.sort(key=lambda x: x.get('last_10_pct', 0) or 0, reverse=reverse)
    elif sort_by == "projection":
        cards.sort(key=lambda x: x.get('projection', 0) or 0, reverse=reverse)
    elif sort_by == "minutes":
        cards.sort(key=lambda x: x.get('expected_minutes', 0) or 0, reverse=reverse)
    else:  # score
        cards.sort(key=lambda x: x.get('score', 0) or 0, reverse=reverse)
    
    # Paginate
    total = len(cards)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        "cards": cards[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/cards/top")
async def get_top_cards(limit: int = Query(20, ge=1, le=100)):
    """Get top scoring cards"""
    cards = data_service.get_player_cards()
    cards.sort(key=lambda x: x.get('score', 0) or 0, reverse=True)
    return {"cards": cards[:limit], "total": len(cards)}


@router.get("/cards/player/{player_name}")
async def get_player_cards(player_name: str):
    """Get all cards for a specific player"""
    cards = data_service.get_player_cards()
    player_cards = [c for c in cards if c.get('name', '').lower() == player_name.lower()]
    if not player_cards:
        # Try partial match
        player_cards = [c for c in cards if player_name.lower() in c.get('name', '').lower()]
    return {"cards": player_cards, "total": len(player_cards)}


# ── Teams & Prop Types ────────────────────────────────────────────────────

@router.get("/teams")
async def get_teams():
    """Get list of all teams"""
    cards = data_service.get_player_cards()
    teams = sorted(set(c.get('team', '') for c in cards if c.get('team')))
    return {"teams": teams}


@router.get("/prop-types")
async def get_prop_types():
    """Get list of all prop types"""
    cards = data_service.get_player_cards()
    props = sorted(set(c.get('prop', '') for c in cards if c.get('prop')))
    return {"props": props}


# ── DVP (Defense vs Position) ─────────────────────────────────────────────

@router.get("/dvp")
async def get_dvp():
    """Get full DVP data"""
    return data_service.get_dvp_weighted()


@router.get("/dvp/{position}")
async def get_dvp_by_position(position: str):
    """Get DVP data for a specific position"""
    dvp = data_service.get_dvp_weighted()
    position = position.upper()
    if position not in dvp:
        raise HTTPException(status_code=404, detail=f"Position {position} not found")
    return dvp[position]


@router.get("/dvp/{position}/{team}")
async def get_dvp_by_position_team(position: str, team: str):
    """Get DVP data for a position against a specific team"""
    dvp = data_service.get_dvp_weighted()
    position = position.upper()
    team = team.upper()
    if position not in dvp:
        raise HTTPException(status_code=404, detail=f"Position {position} not found")
    if team not in dvp[position]:
        raise HTTPException(status_code=404, detail=f"Team {team} not found for position {position}")
    return dvp[position][team]


# ── Gamelogs ──────────────────────────────────────────────────────────────

@router.get("/gamelogs")
async def get_gamelogs(
    player: Optional[str] = None,
    team: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """Get player gamelogs"""
    logs = data_service.get_gamelogs()
    
    if player:
        logs = [g for g in logs if player.lower() in g.get('PLAYER', '').lower()]
    if team:
        logs = [g for g in logs if g.get('TEAM', '').upper() == team.upper()]
    
    # Sort by date descending
    logs.sort(key=lambda x: x.get('GAME DATE', ''), reverse=True)
    
    return {"gamelogs": logs[:limit], "total": len(logs)}


@router.get("/gamelogs/{player_name}")
async def get_player_gamelogs(
    player_name: str,
    limit: int = Query(20, ge=1, le=100),
):
    """Get gamelogs for a specific player"""
    logs = data_service.get_player_gamelogs(player_name, limit)
    return {"gamelogs": logs, "total": len(logs)}


# ── Schedule ──────────────────────────────────────────────────────────────

@router.get("/schedule")
async def get_schedule(
    team: Optional[str] = None,
    date: Optional[str] = None,
):
    """Get NBA schedule"""
    schedule = data_service.get_schedule()
    
    if team:
        schedule = [g for g in schedule if 
                   g.get('home', '').upper() == team.upper() or 
                   g.get('away', '').upper() == team.upper()]
    if date:
        schedule = [g for g in schedule if g.get('date') == date]
    
    return {"games": schedule, "total": len(schedule)}


@router.get("/schedule/today")
async def get_todays_games():
    """Get today's games"""
    games = data_service.get_todays_games()
    return {"games": games, "total": len(games)}


# ── Injuries ──────────────────────────────────────────────────────────────

@router.get("/injuries")
async def get_injuries(
    team: Optional[str] = None,
    status: Optional[str] = None,  # OUT, GTD, etc.
):
    """Get injury report"""
    injuries = data_service.get_injuries()
    
    if team:
        injuries = [i for i in injuries if i.get('team', '').upper() == team.upper()]
    if status:
        injuries = [i for i in injuries if i.get('status', '').upper() == status.upper()]
    
    return {"injuries": injuries, "total": len(injuries)}


@router.get("/injuries/{team}")
async def get_team_injuries(team: str):
    """Get injuries for a specific team"""
    injuries = data_service.get_team_injuries(team)
    return {"injuries": injuries, "total": len(injuries)}


# ── Odds ──────────────────────────────────────────────────────────────────

@router.get("/odds")
async def get_odds():
    """Get latest odds data"""
    return data_service.get_odds_latest()


@router.get("/odds/events")
async def get_odds_events():
    """Get odds events (games with spreads)"""
    odds = data_service.get_odds_latest()
    events = odds.get('events', [])
    return {"events": events, "total": len(events)}


# ── Players ───────────────────────────────────────────────────────────────

@router.get("/players")
async def get_players(
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    """Get all players"""
    players = data_service.get_players()
    
    if search:
        search_lower = search.lower()
        players = [p for p in players if 
                  search_lower in (p.get('full_name', '') or p.get('name', '')).lower()]
    
    return {"players": players[:limit], "total": len(players)}


@router.get("/players/positions")
async def get_player_positions():
    """Get player to position mapping"""
    return data_service.get_player_positions()


@router.get("/players/{player_name}")
async def get_player_full_data(player_name: str):
    """Get comprehensive data for a single player"""
    data = data_service.get_full_player_data(player_name)
    if not data.get('player') and not data.get('props'):
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
    return data


@router.get("/players/slug/{slug}")
async def get_player_by_slug(slug: str):
    """Get player data by URL slug"""
    # Convert slug back to name search
    cards = data_service.get_player_cards()
    
    # Find player whose name matches the slug
    for card in cards:
        name = card.get('name', '')
        if make_slug(name) == slug:
            return data_service.get_full_player_data(name)
    
    raise HTTPException(status_code=404, detail=f"Player with slug '{slug}' not found")


# ── Dashboard & Aggregated ────────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard():
    """Get aggregated dashboard data"""
    return data_service.get_dashboard_data()
