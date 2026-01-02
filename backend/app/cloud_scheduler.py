"""
Cloud Scheduler for NBA Props Data
Runs in Railway with scheduled jobs for:
- Odds: Every 5 minutes
- DVP: Once daily at 6 AM EST
- Gamelogs: Every 2 hours (using API instead of Selenium for cloud)
"""

import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import unicodedata
import re
import math

logger = logging.getLogger(__name__)

# File paths (relative to backend directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'odds')
BACKEND_DATA_DIR = os.path.join(BACKEND_DIR, 'data')

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DATA_DIR, exist_ok=True)

TEAM_NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS",
}


def normalize_name(n):
    nf = unicodedata.normalize('NFKD', n)
    return ''.join(c for c in nf if not unicodedata.combining(c))


def make_slug(name):
    base = normalize_name(name.lower())
    return re.sub(r'[^a-z0-9]+', '-', base).strip('-')


# ============ ODDS FETCHER ============
def fetch_odds():
    """Fetch player prop odds from props.cash API"""
    logger.info("📊 Fetching player prop odds...")
    try:
        url = "https://api.props.cash/nba/lines"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; OddsFetcher/1.0)",
            "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjF0dUkybDZSQjBjWlF2MHM1M28yNSJ9.eyJzdWJzY3JpcHRpb24iOiJwcm8iLCJpc3MiOiJodHRwczovL3Byb3BzLWhlbHBlci51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDc0MjU1MTA0NDAyMTQ2OTc2NzgiLCJhdWQiOlsiaHR0cHM6Ly9wcm9wcy1kb3QtY2FzaC9hcGkiLCJodHRwczovL3Byb3BzLWhlbHBlci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzY1ODI5NjI3LCJleHAiOjE3Njg0MjE2MjcsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJhenAiOiJrSTc2UFlrOUEzZzd5VXR5aFkzQWhLbXI5b3ZpSEF6dyJ9.f2QLyPDiCr6GLVZOPZs_meFPdgviJHixHjb9gLSfXPIT2E2aniB-OXKsmMeSOi6qSfyNmDaOlbLt1h1f7vTNlnTHubciMD3bwUtOqfDQMTof2AlGyJE2FXb3lqSKGXts5cDC-kW2zga1gZ3VsVtGqHj_WedV5NWQaOlKvEjdu8TfPL7HydkABm-TovoWMlANxXQgrInHSMmubvUKNaA8xv4wLGM0jj0kf3xSe2ag6qYPVf6fsdV4pRmvLygYy1WiwolLs6KBxHML_WwAn81AObsipWPy8BFSZAN1w96Frgm0FFF0RvGEJdjFU1lWf6RRNf3VrcWPfwS5NdrKGS8oiw"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Save to file
        odds_path = os.path.join(BASE_DIR, 'nba_player_odds.json')
        with open(odds_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Also save to NBA_PURE_STANDARD_SINGLE.json for compatibility
        single_path = os.path.join(BASE_DIR, 'NBA_PURE_STANDARD_SINGLE.json')
        with open(single_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Odds saved: {len(data) if isinstance(data, list) else 'OK'} records")
        return True
    except Exception as e:
        logger.error(f"❌ Odds fetch failed: {e}")
        return False


# ============ DVP FETCHER ============
def fetch_dvp():
    """Fetch Defense vs Position data from FantasyPros"""
    logger.info("🛡️ Fetching DVP data...")
    try:
        url = "https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php"
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "data-table"})
        
        if not table:
            logger.error("DVP table not found")
            return False
        
        # Get column names
        column_names = [th.text.strip() for th in table.find("tr").find_all("th")]
        
        final_df = pd.DataFrame()
        for pos in positions:
            cl = "GC-30 " + pos
            data = []
            for tr in table.find_all("tr", class_=[cl]):
                row_data = [td.text.strip() for td in tr.find_all("td")]
                team_column = tr.find("td", class_="left team-cell")
                if team_column:
                    team_text = team_column.text.strip()
                    team_code = team_text[:3]
                    if team_code == 'NOR':
                        team_code = 'NOP'
                    team_name = team_text[3:]
                    row_data = [team_code, team_name] + row_data
                data.append(row_data)
            
            df = pd.DataFrame(data, columns=["tsc", "team_name"] + column_names)
            df = df.drop("Team", axis=1, errors="ignore")
            df['tsc'] = df['tsc'].str.upper().replace({'UTH': 'UTA'})
            
            if not df.empty:
                df.columns = df.columns.str.lower()
                df.insert(0, 'pos', pos)
                final_df = pd.concat([final_df, df], ignore_index=True)
        
        # Save CSV
        csv_path = os.path.join(BASE_DIR, 'DVP_2025.csv')
        final_df.to_csv(csv_path, index=False)
        
        # Convert to nested JSON
        dvp_json = {}
        for _, row in final_df.iterrows():
            team = row['tsc']
            pos = row['pos']
            if team not in dvp_json:
                dvp_json[team] = {}
            dvp_json[team][pos] = {k: row[k] for k in row.index if k not in ['tsc', 'pos', 'team_name']}
        
        json_path = os.path.join(BASE_DIR, 'DVP_2025.json')
        with open(json_path, 'w') as f:
            json.dump(dvp_json, f, indent=2)
        
        # Also save weighted version
        weighted_path = os.path.join(BASE_DIR, 'DVP_2025_weighted.json')
        with open(weighted_path, 'w') as f:
            json.dump(dvp_json, f, indent=2)
        
        logger.info(f"✅ DVP data saved for {len(dvp_json)} teams")
        return True
    except Exception as e:
        logger.error(f"❌ DVP fetch failed: {e}")
        return False


# ============ GAMELOGS FETCHER (API-based for cloud) ============
def fetch_gamelogs():
    """Fetch game logs from NBA Stats API (no Selenium needed)"""
    logger.info("📈 Fetching game logs...")
    try:
        # NBA Stats API endpoint
        url = "https://stats.nba.com/stats/leaguegamelog"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.nba.com",
            "Referer": "https://www.nba.com/",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
            "Connection": "keep-alive"
        }
        params = {
            "Counter": 0,
            "DateFrom": "",
            "DateTo": "",
            "Direction": "DESC",
            "LeagueID": "00",
            "PlayerOrTeam": "P",  # Player logs
            "Season": "2025-26",
            "SeasonType": "Regular Season",
            "Sorter": "DATE"
        }
        
        logger.info(f"📡 Requesting: {url}")
        
        # Retry logic for NBA API (can be flaky)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=120)
                logger.info(f"📡 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    break
                elif attempt < max_retries - 1:
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed with status {response.status_code}, retrying...")
                    import time
                    time.sleep(2)
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Attempt {attempt + 1} timed out, retrying...")
                    import time
                    time.sleep(2)
                else:
                    logger.error("❌ All retry attempts timed out")
                    return False
            except Exception as e:
                logger.error(f"❌ Request error: {e}")
                return False
        
        if response.status_code != 200:
            logger.error(f"❌ NBA API returned status {response.status_code}: {response.text[:500]}")
            return False
            
        response.raise_for_status()
        data = response.json()
        
        # Parse the response
        result_set = data.get('resultSets', [{}])[0]
        headers_list = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])
        
        if not rows:
            logger.warning("No gamelog data returned from API")
            return False
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers_list)
        
        # Rename columns to match existing format
        column_mapping = {
            'PLAYER_NAME': 'PLAYER NAME',
            'GAME_DATE': 'GAME DATE',
            'MATCHUP': 'MATCHUP',
            'WL': 'W/L',
            'MIN': 'MIN',
            'PTS': 'PTS',
            'REB': 'REB',
            'AST': 'AST',
            'STL': 'STL',
            'BLK': 'BLK',
            'TOV': 'TOV',
            'FGM': 'FGM',
            'FGA': 'FGA',
            'FG_PCT': 'FG%',
            'FG3M': '3PM',
            'FG3A': '3PA',
            'FG3_PCT': '3P%',
            'FTM': 'FTM',
            'FTA': 'FTA',
            'FT_PCT': 'FT%',
            'OREB': 'OREB',
            'DREB': 'DREB',
            'PLUS_MINUS': '+/-',
        }
        df = df.rename(columns=column_mapping)
        
        # Save CSV to both locations
        csv_path = os.path.join(BASE_DIR, 'Full_Gamelogs25.csv')
        df.to_csv(csv_path, index=False)
        logger.info(f"📁 Saved gamelogs to: {csv_path}")
        
        # Also save to backend data dir
        csv_path_backend = os.path.join(BACKEND_DATA_DIR, 'Full_Gamelogs25.csv')
        df.to_csv(csv_path_backend, index=False)
        logger.info(f"📁 Also saved to: {csv_path_backend}")
        
        # Save JSON
        def replace_nan(obj):
            if isinstance(obj, dict):
                return {k: replace_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_nan(v) for v in obj]
            elif isinstance(obj, float) and (math.isnan(obj) if obj == obj else True):
                return None
            else:
                return obj
        
        json_path = os.path.join(BASE_DIR, 'Player_Gamelogs25.json')
        gamelogs = df.to_dict(orient='records')
        with open(json_path, 'w') as f:
            json.dump(replace_nan(gamelogs), f, indent=2)
        
        logger.info(f"✅ Gamelogs saved: {len(df)} records")
        return True
    except Exception as e:
        logger.error(f"❌ Gamelogs fetch failed: {e}")
        return False


# ============ SCHEDULE FETCHER ============
def fetch_schedule():
    """Fetch today's NBA schedule"""
    logger.info("📅 Fetching NBA schedule...")
    try:
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        
        url = f"https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        schedule_path = os.path.join(BASE_DIR, 'nba_schedule.json')
        with open(schedule_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("✅ Schedule saved")
        return True
    except Exception as e:
        logger.error(f"❌ Schedule fetch failed: {e}")
        return False


# ============ BUILD CARDS ============
def build_player_cards():
    """Rebuild player cards with latest data"""
    logger.info("🏗️ Building player cards...")
    try:
        # Load odds
        odds_path = os.path.join(BASE_DIR, 'NBA_PURE_STANDARD_SINGLE.json')
        if not os.path.exists(odds_path):
            # Try alternate path
            odds_path = os.path.join(BASE_DIR, 'nba_player_odds.json')
            if not os.path.exists(odds_path):
                logger.error("Odds file not found")
                return False
        
        with open(odds_path) as f:
            raw = json.load(f)
        
        logger.info(f"📊 Loaded odds data: type={type(raw).__name__}, len={len(raw) if isinstance(raw, (list, dict)) else 'N/A'}")
        
        # Load spreads
        spreads_path = os.path.join(DATA_DIR, 'latest.json')
        team_spreads = {}
        if os.path.exists(spreads_path):
            with open(spreads_path) as f:
                odds_data = json.load(f)
            events = odds_data.get('events', [])
            for ev in events:
                for side in ['home', 'away']:
                    team_full = ev.get(f'{side}_team')
                    spread = None
                    spread_obj = ev.get('best_spread', {}).get(side)
                    if spread_obj and 'point' in spread_obj:
                        spread = spread_obj['point']
                    if team_full and spread is not None:
                        team_abbr = TEAM_NAME_TO_ABBR.get(team_full, team_full)
                        team_spreads[team_abbr] = spread
        
        # Load schedule to get opponents
        schedule_path = os.path.join(BACKEND_DATA_DIR, 'nba_schedule.json')
        if not os.path.exists(schedule_path):
            schedule_path = os.path.join(BASE_DIR, 'nba_schedule.json')
        team_opponents = {}
        if os.path.exists(schedule_path):
            try:
                with open(schedule_path) as f:
                    schedule_raw = json.load(f)
                # Handle NBA's complex schedule format
                if isinstance(schedule_raw, dict) and 'leagueSchedule' in schedule_raw:
                    # NBA Stats format - need to parse gameDates
                    from datetime import date
                    today_str = date.today().strftime("%m/%d/%Y")
                    game_dates = schedule_raw.get('leagueSchedule', {}).get('gameDates', [])
                    for gd in game_dates:
                        game_date = gd.get('gameDate', '')
                        if not game_date.startswith(today_str.split(' ')[0][:5]):
                            continue
                        for game in gd.get('games', []):
                            home_team = game.get('homeTeam', {})
                            away_team = game.get('awayTeam', {})
                            home = home_team.get('teamTricode', '')
                            away = away_team.get('teamTricode', '')
                            if home and away:
                                team_opponents[home] = away
                                team_opponents[away] = home
                elif isinstance(schedule_raw, list):
                    # Simple list format from backend/data
                    for game in schedule_raw:
                        if isinstance(game, dict):
                            home = game.get('home', '')
                            away = game.get('away', '')
                            if home and away:
                                team_opponents[home] = away
                                team_opponents[away] = home
            except Exception as e:
                logger.warning(f"⚠️ Schedule parsing failed: {e} - continuing without opponent data")
        
        # Load DVP data for rankings
        dvp_data = {}
        dvp_path = os.path.join(BACKEND_DATA_DIR, 'DVP_2025_weighted.json')
        logger.info(f"📊 Looking for DVP at BACKEND_DATA_DIR: {dvp_path}, exists={os.path.exists(dvp_path)}")
        if not os.path.exists(dvp_path):
            dvp_path = os.path.join(BASE_DIR, 'DVP_2025_weighted.json')
            logger.info(f"📊 Looking for DVP at BASE_DIR: {dvp_path}, exists={os.path.exists(dvp_path)}")
        if os.path.exists(dvp_path):
            with open(dvp_path) as f:
                dvp_data = json.load(f)
            logger.info(f"📊 Loaded DVP data with {len(dvp_data)} positions")
        else:
            logger.warning(f"⚠️ DVP file not found at any path!")
        
        # Load player positions
        positions_data = {}
        positions_path = os.path.join(BACKEND_DATA_DIR, 'nba_players_2025_26_positions.json')
        if not os.path.exists(positions_path):
            positions_path = os.path.join(BASE_DIR, 'nba_players_2025_26_positions.json')
        if os.path.exists(positions_path):
            with open(positions_path) as f:
                positions_data = json.load(f)
        
        # Load gamelogs - try multiple paths
        gamelogs_path = os.path.join(BASE_DIR, 'Full_Gamelogs25.csv')
        if not os.path.exists(gamelogs_path):
            gamelogs_path = os.path.join(BACKEND_DATA_DIR, 'Full_Gamelogs25.csv')
        if not os.path.exists(gamelogs_path):
            logger.error(f"Gamelogs file not found at BASE_DIR or BACKEND_DATA_DIR")
            logger.error(f"Checked paths: {os.path.join(BASE_DIR, 'Full_Gamelogs25.csv')}, {os.path.join(BACKEND_DATA_DIR, 'Full_Gamelogs25.csv')}")
            return False
        
        logger.info(f"📁 Loading gamelogs from: {gamelogs_path}")
        df_logs = pd.read_csv(gamelogs_path)
        
        # Normalize column name for player (CSV may have 'PLAYER' instead of 'PLAYER NAME')
        if 'PLAYER' in df_logs.columns and 'PLAYER NAME' not in df_logs.columns:
            df_logs['PLAYER NAME'] = df_logs['PLAYER']
        
        # Build player_id lookup from gamelogs (use normalized names for matching)
        player_ids = {}
        if 'PLAYER_ID' in df_logs.columns:
            for _, row in df_logs[['PLAYER NAME', 'PLAYER_ID']].drop_duplicates().iterrows():
                # Store with both original and normalized name for flexible matching
                original_name = row['PLAYER NAME']
                normalized_key = normalize_name(original_name).lower()
                player_ids[original_name] = int(row['PLAYER_ID'])
                player_ids[normalized_key] = int(row['PLAYER_ID'])
        df_logs['GAME DATE'] = pd.to_datetime(df_logs['GAME DATE'])
        logger.info(f"📈 Loaded gamelogs: {len(df_logs)} records")
        
        # Stat mapping (maps stat names to gamelog columns)
        STAT_MAP = {
            'points': ['PTS'], 'rebounds': ['REB'], 'assists': ['AST'],
            'threes': ['3PM'], '3pm': ['3PM'], 'steals': ['STL'], 'blocks': ['BLK'],
            'pts_rebs_asts': ['PTS', 'REB', 'AST'], 'pra': ['PTS', 'REB', 'AST'],
            'pts_asts': ['PTS', 'AST'], 'pa': ['PTS', 'AST'],
            'pts_rebs': ['PTS', 'REB'], 'pr': ['PTS', 'REB'],
            'rebs_asts': ['REB', 'AST'], 'ra': ['REB', 'AST'],
            'stls_blks': ['STL', 'BLK'], 'sb': ['STL', 'BLK'],
            'turnovers': ['TOV'],
            # Capitalized versions
            'Points': ['PTS'], 'Rebounds': ['REB'], 'Assists': ['AST'],
            'Threes': ['3PM'], '3PM': ['3PM'], 'Steals': ['STL'], 'Blocks': ['BLK'],
        }
        
        # Build cards - handle both flat and nested structures
        cards = []
        
        # Normalize structure - props.cash returns a list where each item is a player with nested projections
        if isinstance(raw, list):
            pp_lines = raw
        elif isinstance(raw, dict):
            if 'lines' in raw:
                pp_lines = raw['lines']
            elif 'data' in raw:
                pp_lines = raw['data']
            else:
                pp_lines = list(raw.values())
        else:
            pp_lines = []
        
        logger.info(f"📋 Processing {len(pp_lines)} player lines")
        
        # DVP stat key mapping
        DVP_STAT_MAP = {
            'points': 'pts', 'rebounds': 'reb', 'assists': 'ast',
            'steals': 'stl', 'blocks': 'blk', 'turnovers': 'to',
            'threes': '3pm', '3pm': '3pm',
            'pts_rebs_asts': 'pra', 'pra': 'pra',
            'pts_asts': 'pa', 'pa': 'pa',
            'pts_rebs': 'pr', 'pr': 'pr',
            'rebs_asts': 'ra', 'ra': 'ra',
        }
        
        def get_dvp_rank(opponent, position, stat_key):
            """Get DVP rank for a stat against a position"""
            if not opponent or not position or not dvp_data:
                return None
            dvp_stat = DVP_STAT_MAP.get(stat_key.lower(), stat_key.lower())
            pos_data = dvp_data.get(position, {})
            team_data = pos_data.get(opponent, {})
            stat_data = team_data.get(dvp_stat, {})
            return stat_data.get('rank')
        
        def calculate_hit_rates(p_logs_copy, line_value):
            """Calculate hit rates for L5, L10, L20, season"""
            l5 = p_logs_copy.head(5)
            l10 = p_logs_copy.head(10)
            l20 = p_logs_copy.head(20)
            season = p_logs_copy
            
            def calc(df, line_val):
                if len(df) == 0:
                    return 0, 0, "0-0"
                hits = (df['combined'] > line_val).sum()
                pct = (hits / len(df)) * 100
                record = f"{hits}-{len(df)}"
                return round(pct, 1), hits, record
            
            l5_pct, l5_hits, l5_rec = calc(l5, line_value)
            l10_pct, l10_hits, l10_rec = calc(l10, line_value)
            l20_pct, l20_hits, l20_rec = calc(l20, line_value)
            season_pct, season_hits, season_rec = calc(season, line_value)
            
            return {
                'last_5_pct': l5_pct, 'last_5': l5_rec,
                'last_10_pct': l10_pct, 'last_10': l10_rec,
                'last_20_pct': l20_pct, 'last_20': l20_rec,
                'season_pct': season_pct, 'season': season_rec,
            }
        
        for line in pp_lines:
            # Get player info
            player_name = line.get('name', line.get('player_name', line.get('player', '')))
            if not player_name:
                continue
            
            team = line.get('team', '')
            position = line.get('position', '') or positions_data.get(player_name, '')
            
            # Get opponent from schedule
            opponent = team_opponents.get(team, '')
            
            # Get player_id from gamelogs (try exact match first, then normalized)
            player_id = player_ids.get(player_name)
            if player_id is None:
                player_id = player_ids.get(normalize_name(player_name).lower())
            
            # Get player logs
            p_logs = df_logs[df_logs['PLAYER NAME'].str.lower() == player_name.lower()]
            if p_logs.empty:
                # Try normalized name matching
                p_logs = df_logs[df_logs['PLAYER NAME'].apply(normalize_name).str.lower() == normalize_name(player_name).lower()]
            
            if p_logs.empty:
                continue
            
            # Sort by date for proper window calculations
            p_logs = p_logs.sort_values('GAME DATE', ascending=False)
            
            # Calculate expected minutes (weighted average like update_all_cards.py)
            expected_minutes = 0
            if 'MIN' in p_logs.columns:
                min_values = pd.to_numeric(p_logs['MIN'], errors='coerce').dropna().tolist()
                min_values = [min(max(0, v), 60) for v in min_values]  # Clamp 0-60
                if min_values:
                    def minutes_avg(vals, n=None):
                        slice_vals = vals[:n] if n else vals
                        return sum(slice_vals) / len(slice_vals) if slice_vals else 0
                    min_l5 = minutes_avg(min_values, 5)
                    min_l10 = minutes_avg(min_values, 10)
                    min_l20 = minutes_avg(min_values, 20)
                    min_season = minutes_avg(min_values)
                    expected_minutes = round(
                        min_l5 * 0.30 +
                        min_l10 * 0.40 +
                        min_l20 * 0.20 +
                        min_season * 0.10, 1
                    )
            
            # Handle nested projection structure from props.cash
            projection = line.get('projection', {})
            if isinstance(projection, dict):
                # Process each stat type in the projection
                for stat_key, stat_data in projection.items():
                    if not isinstance(stat_data, dict):
                        continue
                    
                    # Get the line value from summary
                    summary = stat_data.get('summary', {})
                    line_value = summary.get('manualOU') or summary.get('line') or summary.get('value')
                    if line_value is None:
                        continue
                    
                    # Get odds
                    over_price = summary.get('overPrice', 0)
                    under_price = summary.get('underPrice', 0)
                    
                    # Map stat key to gamelog columns
                    cols = STAT_MAP.get(stat_key.lower(), [stat_key.upper()])
                    valid_cols = [c for c in cols if c in p_logs.columns]
                    if not valid_cols:
                        continue
                    
                    p_logs_copy = p_logs.copy()
                    p_logs_copy['combined'] = p_logs_copy[valid_cols].sum(axis=1)
                    
                    # Get last 10 values for bar chart (oldest to newest)
                    last_10_values = p_logs_copy.head(10)['combined'].tolist()[::-1]
                    
                    # Recent games
                    recent = p_logs_copy.nlargest(10, 'GAME DATE')
                    if recent.empty:
                        continue
                    
                    avg = recent['combined'].mean()
                    median = recent['combined'].median()
                    hit_count = (recent['combined'] > line_value).sum()
                    hit_rate = hit_count / len(recent) * 100
                    
                    spread = team_spreads.get(team, 0)
                    
                    # Get DVP rank
                    dvp_rank = get_dvp_rank(opponent, position, stat_key)
                    
                    # Calculate all hit rates
                    hit_rates = calculate_hit_rates(p_logs_copy, line_value)
                    
                    # Build card
                    card = {
                        'name': player_name,
                        'player_name': player_name,
                        'player_slug': make_slug(player_name),
                        'team': team,
                        'opponent': opponent,
                        'position': position,
                        'player_id': player_id,
                        'prop': stat_key.replace('_', '+').title(),
                        'stat_type': stat_key,
                        'line': float(line_value),
                        'projection': round(avg, 1),
                        'avg': round(avg, 1),
                        'median': round(median, 1),
                        'hit_rate': round(hit_rate, 1),
                        'last_5_pct': hit_rates['last_5_pct'],
                        'last_5': hit_rates['last_5'],
                        'last_10_pct': hit_rates['last_10_pct'],
                        'last_10': hit_rates['last_10'],
                        'last_20_pct': hit_rates['last_20_pct'],
                        'last_20': hit_rates['last_20'],
                        'season_pct': hit_rates['season_pct'],
                        'season': hit_rates['season'],
                        'last_10_values': last_10_values,
                        'hit_count': int(hit_count),
                        'games_played': len(p_logs_copy),
                        'games': len(p_logs_copy),
                        'spread': spread,
                        'dvp_rank': dvp_rank,
                        'over_odds': over_price,
                        'under_odds': under_price,
                        'expected_minutes': expected_minutes,
                        'score': round((hit_rate * 0.4) + (min(avg / max(line_value, 1), 1.5) * 40) + (20 if spread < -3 else 10 if spread < 0 else 0), 1),
                        'last_updated': datetime.now().isoformat()
                    }
                    cards.append(card)
            else:
                # Handle flat structure (old format)
                stat_type = line.get('stat', line.get('stat_type', ''))
                line_value = line.get('line', line.get('value', 0))
                
                if not stat_type or not line_value:
                    continue
                
                cols = STAT_MAP.get(stat_type.lower(), [stat_type.upper()])
                valid_cols = [c for c in cols if c in p_logs.columns]
                if not valid_cols:
                    continue
                
                p_logs_copy = p_logs.copy()
                p_logs_copy['combined'] = p_logs_copy[valid_cols].sum(axis=1)
                
                # Get last 10 values for bar chart (oldest to newest)
                last_10_values = p_logs_copy.head(10)['combined'].tolist()[::-1]
                
                recent = p_logs_copy.nlargest(10, 'GAME DATE')
                if recent.empty:
                    continue
                
                avg = recent['combined'].mean()
                median = recent['combined'].median()
                hit_count = (recent['combined'] > line_value).sum()
                hit_rate = hit_count / len(recent) * 100
                spread = team_spreads.get(team, 0)
                
                # Get DVP rank
                dvp_rank = get_dvp_rank(opponent, position, stat_type)
                
                # Calculate all hit rates
                hit_rates = calculate_hit_rates(p_logs_copy, line_value)
                
                card = {
                    'name': player_name,
                    'player_name': player_name,
                    'player_slug': make_slug(player_name),
                    'team': team,
                    'opponent': opponent,
                    'position': position,
                    'player_id': player_id,
                    'prop': stat_type,
                    'stat_type': stat_type,
                    'line': float(line_value),
                    'projection': round(avg, 1),
                    'avg': round(avg, 1),
                    'median': round(median, 1),
                    'hit_rate': round(hit_rate, 1),
                    'last_5_pct': hit_rates['last_5_pct'],
                    'last_5': hit_rates['last_5'],
                    'last_10_pct': hit_rates['last_10_pct'],
                    'last_10': hit_rates['last_10'],
                    'last_20_pct': hit_rates['last_20_pct'],
                    'last_20': hit_rates['last_20'],
                    'season_pct': hit_rates['season_pct'],
                    'season': hit_rates['season'],
                    'last_10_values': last_10_values,
                    'hit_count': int(hit_count),
                    'games_played': len(p_logs_copy),
                    'games': len(p_logs_copy),
                    'spread': spread,
                    'dvp_rank': dvp_rank,
                    'expected_minutes': expected_minutes,
                    'score': round((hit_rate * 0.4) + (min(avg / max(line_value, 1), 1.5) * 40) + (20 if spread < -3 else 10 if spread < 0 else 0), 1),
                    'last_updated': datetime.now().isoformat()
                }
                cards.append(card)
        
        # Save cards
        cards_path = os.path.join(BASE_DIR, 'PLAYER_UI_CARDS_PERFECT.json')
        with open(cards_path, 'w') as f:
            json.dump(cards, f, indent=2)
        
        logger.info(f"✅ Built {len(cards)} player cards")
        return True
    except Exception as e:
        logger.error(f"❌ Card build failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


# ============ MASTER UPDATE ============
def run_full_update():
    """Run all data updates and rebuild cards"""
    logger.info("🚀 Starting full data update...")
    
    # Fetch all data
    fetch_odds()
    fetch_schedule()
    
    # Build cards
    build_player_cards()
    
    logger.info("✅ Full update complete")


def run_daily_update():
    """Daily update (DVP + gamelogs)"""
    logger.info("📆 Starting daily update...")
    fetch_dvp()
    fetch_gamelogs()
    run_full_update()
    logger.info("✅ Daily update complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_full_update()
