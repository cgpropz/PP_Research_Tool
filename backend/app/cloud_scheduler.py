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
DATA_DIR = os.path.join(BASE_DIR, 'data', 'odds')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.nba.com",
            "Referer": "https://www.nba.com/",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true"
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
        
        response = requests.get(url, headers=headers, params=params, timeout=60)
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
        
        # Save CSV
        csv_path = os.path.join(BASE_DIR, 'Full_Gamelogs25.csv')
        df.to_csv(csv_path, index=False)
        
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
            logger.error("Odds file not found")
            return False
        
        with open(odds_path) as f:
            raw = json.load(f)
        
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
        
        # Normalize structure
        if isinstance(raw, dict):
            if 'lines' in raw and isinstance(raw['lines'], list):
                pp_lines = raw['lines']
            elif 'data' in raw and isinstance(raw['data'], list):
                pp_lines = raw['data']
            else:
                pp_lines = [v for v in raw.values() if isinstance(v, dict)]
        else:
            pp_lines = raw if isinstance(raw, list) else []
        
        # Load gamelogs
        gamelogs_path = os.path.join(BASE_DIR, 'Full_Gamelogs25.csv')
        if not os.path.exists(gamelogs_path):
            logger.error("Gamelogs file not found")
            return False
        
        df_logs = pd.read_csv(gamelogs_path)
        df_logs['GAME DATE'] = pd.to_datetime(df_logs['GAME DATE'])
        
        # Stat mapping
        STAT_MAP = {
            'Points': ['PTS'], 'Rebounds': ['REB'], 'Assists': ['AST'],
            'Threes': ['3PM'], '3PM': ['3PM'], 'Steals': ['STL'], 'Blocks': ['BLK'],
            'Pts+Rebs+Asts': ['PTS', 'REB', 'AST'], 'PRA': ['PTS', 'REB', 'AST'],
            'Pts+Asts': ['PTS', 'AST'], 'PA': ['PTS', 'AST'],
            'Pts+Rebs': ['PTS', 'REB'], 'PR': ['PTS', 'REB'],
            'Rebs+Asts': ['REB', 'AST'], 'RA': ['REB', 'AST'],
            'Stls+Blks': ['STL', 'BLK'], 'SB': ['STL', 'BLK'],
            'Turnovers': ['TOV']
        }
        
        # Build cards
        cards = []
        for line in pp_lines:
            player_name = line.get('player_name', line.get('player', ''))
            if not player_name:
                continue
            
            stat_type = line.get('stat_type', line.get('stat', ''))
            line_value = line.get('line', line.get('value', 0))
            
            # Get player logs
            p_logs = df_logs[df_logs['PLAYER NAME'].str.lower() == player_name.lower()]
            if p_logs.empty:
                continue
            
            # Calculate stats
            cols = STAT_MAP.get(stat_type, [stat_type.upper()])
            valid_cols = [c for c in cols if c in p_logs.columns]
            if not valid_cols:
                continue
            
            p_logs = p_logs.copy()
            p_logs['combined'] = p_logs[valid_cols].sum(axis=1)
            
            # Recent games
            recent = p_logs.nlargest(10, 'GAME DATE')
            if recent.empty:
                continue
            
            avg = recent['combined'].mean()
            median = recent['combined'].median()
            hit_count = (recent['combined'] > line_value).sum()
            hit_rate = hit_count / len(recent) * 100
            
            # Get team
            team = recent.iloc[0].get('MATCHUP', '')[:3] if len(recent) > 0 else ''
            spread = team_spreads.get(team, 0)
            
            # Build card
            card = {
                'player_name': player_name,
                'player_slug': make_slug(player_name),
                'team': team,
                'stat_type': stat_type,
                'line': line_value,
                'projection': round(avg, 1),
                'median': round(median, 1),
                'hit_rate': round(hit_rate, 1),
                'hit_count': int(hit_count),
                'games_played': len(recent),
                'spread': spread,
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
