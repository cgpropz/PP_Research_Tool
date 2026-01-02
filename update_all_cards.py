import os
import json
import pandas as pd
import unicodedata
import re
from datetime import datetime
import subprocess
import sys
import math
# Import the odds fetcher
import fetch_nba_props_cash_odds

def normalize_name(n):
    nf = unicodedata.normalize('NFKD', n)
    return ''.join(c for c in nf if not unicodedata.combining(c))

def make_slug(name):
    base = normalize_name(name.lower())
    return re.sub(r'[^a-z0-9]+', '-', base).strip('-')

# Map full team names to abbreviations
TEAM_NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS",
}

def build_player_cards():
    # Load odds and gamelogs
    with open('NBA_PURE_STANDARD_SINGLE.json') as f:
        raw = json.load(f)
    # Load spreads from odds file
    odds_path = os.path.join('data', 'odds', 'latest.json')
    if os.path.exists(odds_path):
        with open(odds_path) as f:
            odds_data = json.load(f)
        events = odds_data.get('events', [])
        # Build team to spread map (using abbreviations)
        team_spreads = {}
        for ev in events:
            for side in ['home', 'away']:
                team_full = ev.get(f'{side}_team')
                spread = None
                spread_obj = ev.get('best_spread', {}).get(side)
                if spread_obj and 'point' in spread_obj:
                    spread = spread_obj['point']
                if team_full and spread is not None:
                    # Convert full name to abbreviation
                    team_abbr = TEAM_NAME_TO_ABBR.get(team_full, team_full)
                    team_spreads[team_abbr] = spread
    else:
        team_spreads = {}
    # Normalize structure to list of dicts
    if isinstance(raw, dict):
        if 'lines' in raw and isinstance(raw['lines'], list):
            pp_lines = raw['lines']
        elif 'data' in raw and isinstance(raw['data'], list):
            pp_lines = raw['data']
        else:
            pp_lines = [v for v in raw.values() if isinstance(v, dict)]
    else:
        pp_lines = raw if isinstance(raw, list) else []
    df_logs = pd.read_csv('Full_Gamelogs25.csv')
    df_logs['GAME DATE'] = pd.to_datetime(df_logs['GAME DATE'])
    # Stat mapping
    STAT_MAP = {
        'Points': ['PTS'],
        'Rebounds': ['REB'],
        'Assists': ['AST'],
        'Threes': ['3PM'],
        '3PM': ['3PM'],
        'Steals': ['STL'],
        'Blocks': ['BLK'],
        'Turnovers': ['TOV'],
        'Fantasy Score': ['FANTASY_PTS'],
        'Threes Made': ['3PM'],
        'Three Pointers Made': ['3PM'],
        'Blocked Shots': ['BLK'],
        'Steals + Blocks': ['STL','BLK'],
        # Attempts and granular rebounds
        '2PT Att': ['FGA','3PA'],
        '3PT Att': ['3PA'],
        'FG Att': ['FGA'],
        'Defensive Rebounds': ['DREB'],
        'Offensive Rebounds': ['OREB'],
        'PRA': ['PTS','REB','AST'],
        'Pts+Rebs+Asts': ['PTS','REB','AST'],
        'Pts+Rebs': ['PTS','REB'],
        'Pts+Asts': ['PTS','AST'],
        'Rebs+Asts': ['REB','AST']
    }
    # Load player IDs
    with open('players.json', 'r') as f:
        players = json.load(f)
    name_to_id = {}
    for p in players:
        name = p.get('name') or p.get('full_name')
        if name:
            name_to_id[name.strip().lower()] = p['id']
    def get_player_id(name):
        if not name:
            return None
        return name_to_id.get(name.strip().lower())
    ui_cards = []
    base_projections = {}
    for prop in pp_lines:
        if not isinstance(prop, dict):
            continue
        name = prop.get('Name') or prop.get('name') or prop.get('Player') or prop.get('player')
        team = prop.get('Team') or prop.get('team')
        stat = prop.get('Stat') or prop.get('stat') or prop.get('Prop') or prop.get('prop')
        line = prop.get('Line') or prop.get('line') or prop.get('Value') or prop.get('value')
        opponent = prop.get('Versus') or prop.get('versus') or prop.get('Opponent') or prop.get('opponent') or '???'
        if name is None or stat is None or line is None:
            continue
        if stat not in STAT_MAP:
            continue
        cols = STAT_MAP[stat]
        player_df = df_logs[df_logs['PLAYER NAME'] == name].copy()
        if player_df.empty or len(player_df) < 5:
            continue
        player_df = player_df.sort_values('GAME DATE', ascending=False)
        MIN_COL = 'MIN'
        minutes_values = []
        if MIN_COL in player_df.columns:
            for v in player_df[MIN_COL].tolist():
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    continue
                if fv < 0:
                    continue
                minutes_values.append(min(fv, 60.0))
        # Get spread for player's team
        spread_val = team_spreads.get(team)
        def minutes_avg(vals, n=None):
            if not vals:
                return 0.0
            slice_vals = vals[:n] if (n is not None and n > 0) else vals
            return sum(slice_vals) / len(slice_vals) if slice_vals else 0.0
        min_l5 = minutes_avg(minutes_values, 5)
        min_l10 = minutes_avg(minutes_values, 10)
        min_l20 = minutes_avg(minutes_values, 20)
        min_season = minutes_avg(minutes_values, None)
        expected_minutes = round(
            min_l5 * 0.30 +
            min_l10 * 0.40 +
            min_l20 * 0.20 +
            min_season * 0.10, 1
        )
        # Special handling for derived props
        if stat == '2PT Att':
            fga_vals = player_df['FGA'].astype(float).tolist()
            three_pa_vals = player_df['3PA'].astype(float).tolist()
            values = [max(0, fga - three_pa) for fga, three_pa in zip(fga_vals, three_pa_vals)]
        elif len(cols) == 1:
            values = player_df[cols[0]].astype(float).tolist()
        else:
            values = (player_df[cols].astype(float).sum(axis=1)).tolist()
        def hit_rate(n):
            if len(values) < n:
                hits = sum(1 for v in values[:n] if v > line)
                return hits, len(values[:n])
            else:
                hits = sum(1 for v in values[:n] if v > line)
                return hits, n
        l5_hits, l5_games = hit_rate(5)
        l10_hits, l10_games = hit_rate(10)
        l20_hits, l20_games = hit_rate(20)
        season_hits = sum(1 for v in values if v > line)
        season_games = len(values)
        last_10_values = (values[:10][::-1]) if values else []
        def window_avg(vals, n):
            if not vals:
                return 0.0
            return sum(vals[:n]) / min(n, len(vals))
        l5_avg = window_avg(values, 5)
        l10_avg = window_avg(values, 10)
        l20_avg = window_avg(values, 20)
        season_avg = sum(values)/len(values) if values else 0.0
        weighted_projection = round(
            l5_avg * 0.30 +
            l10_avg * 0.40 +
            l20_avg * 0.20 +
            season_avg * 0.10, 2
        )
        if stat in ['Points','Rebounds','Assists']:
            base_projections[(name, stat)] = weighted_projection
        if stat == 'PRA':
            display_stat = 'Pts+Rebs+Asts'
        elif stat in ['Threes','Threes Made','Three Pointers Made']:
            display_stat = '3PM'
        else:
            display_stat = stat
        combo_projection = None
        if display_stat in ['Pts+Rebs','Pts+Asts','Rebs+Asts','Pts+Rebs+Asts']:
            parts = []
            if display_stat == 'Pts+Rebs':
                parts = ['Points','Rebounds']
            elif display_stat == 'Pts+Asts':
                parts = ['Points','Assists']
            elif display_stat == 'Rebs+Asts':
                parts = ['Rebounds','Assists']
            elif display_stat == 'Pts+Rebs+Asts':
                parts = ['Points','Rebounds','Assists']
            s = 0.0
            have_any = False
            for p in parts:
                bp = base_projections.get((name, p))
                if bp is not None:
                    s += bp
                    have_any = True
            if have_any:
                combo_projection = round(s, 2)
        projection = combo_projection if combo_projection is not None else weighted_projection
        try:
            line_val = float(line)
            proj_val = float(projection)
            score = round(proj_val / line_val * 50, 2) if line_val > 0 else None
        except (TypeError, ValueError):
            score = None
        card = {
            "name": name,
            "team": team,
            "opponent": opponent,
            "prop": display_stat,
            "line": line,
            "last_5": f"{l5_hits}/{l5_games}",
            "last_5_pct": round(l5_hits / l5_games * 100, 1),
            "last_10": f"{l10_hits}/{l10_games}",
            "last_10_pct": round(l10_hits / l10_games * 100, 1),
            "last_20": f"{l20_hits}/{l20_games}",
            "last_20_pct": round(l20_hits / l20_games * 100, 1),
            "season": f"{season_hits}/{season_games}",
            "season_pct": round(season_hits / season_games * 100, 1),
            "avg": round(sum(values)/len(values), 1),
            "games": season_games,
            "last_10_values": last_10_values,
            "projection": projection,
            "expected_minutes": expected_minutes if expected_minutes is not None else 0,
            "player_id": get_player_id(name),
            "score": score,
            "spread": spread_val
        }
        ui_cards.append(card)
    ui_cards = sorted(ui_cards, key=lambda x: x['last_10_pct'], reverse=True)
    with open('PLAYER_UI_CARDS_PERFECT.json', 'w') as f:
        json.dump(replace_nan(ui_cards), f, indent=2)
    print(f"MASTERPIECE COMPLETE → {len(ui_cards)} elite player cards built!")

def replace_nan(obj):
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj

def update_html_timestamp():
    with open('props-trend.html', 'r') as f:
        html = f.read()
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    if '<!--LAST_UPDATED-->' in html:
        html = html.replace('<!--LAST_UPDATED-->', f'Last updated: {timestamp}')
    with open('props-trend.html', 'w') as f:
        f.write(html)

if __name__ == '__main__':
    # Run the NBA schedule and injuries fetchers first
    subprocess.run([sys.executable, 'fetch_nba_schedule.py'], check=True)
    subprocess.run([sys.executable, 'fetch_nba_injuries.py'], check=True)
    # Run the NBA props.cash odds fetcher
    fetch_nba_props_cash_odds.run()
    # Run the PrizePicks odds fetch script to update NBA_PURE_STANDARD_SINGLE.json
    subprocess.run([sys.executable, 'Fetch_PP_Odds.py'], check=True)
    # Run the odds fetcher for spreads
    subprocess.run([sys.executable, os.path.join('players-props','scripts', 'fetch_odds_daily.py')], check=True)  # Removed as requested
    build_player_cards()
    update_html_timestamp()
    # Generate player detail pages for props dashboard
    subprocess.run([sys.executable, os.path.join('players-props', 'scripts', 'generate_player_pages_props.py')], check=True)
    print('All data, HTML, and player pages updated!')
