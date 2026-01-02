#!/usr/bin/env python3
import os
import sys
import json
import time
import datetime as dt
from typing import Dict, Any, List

import urllib.request

API_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=c0bf763840be9b01a9be435c17ba20cb&regions=us&markets=h2h,spreads&oddsFormat=american"
# Go up two levels from scripts/fetch_odds_daily.py to reach workspace root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(ROOT, "data", "odds")
LOGO_DIR = os.path.join(ROOT, "assets", "team-logos")

# Map full team names to ESPN scoreboard abbreviations
TEAM_ABBR = {
    "Atlanta Hawks": "atl",
    "Boston Celtics": "bos",
    "Brooklyn Nets": "bkn",
    "Charlotte Hornets": "cha",
    "Chicago Bulls": "chi",
    "Cleveland Cavaliers": "cle",
    "Dallas Mavericks": "dal",
    "Denver Nuggets": "den",
    "Detroit Pistons": "det",
    "Golden State Warriors": "gsw",
    "Houston Rockets": "hou",
    "Indiana Pacers": "ind",
    "Los Angeles Clippers": "lac",
    "Los Angeles Lakers": "lal",
    "Memphis Grizzlies": "mem",
    "Miami Heat": "mia",
    "Milwaukee Bucks": "mil",
    "Minnesota Timberwolves": "min",
    "New Orleans Pelicans": "nop",
    "New York Knicks": "nyk",
    "Oklahoma City Thunder": "okc",
    "Orlando Magic": "orl",
    "Philadelphia 76ers": "phi",
    "Phoenix Suns": "phx",
    "Portland Trail Blazers": "por",
    "Sacramento Kings": "sac",
    "San Antonio Spurs": "sas",
    "Toronto Raptors": "tor",
    "Utah Jazz": "uta",
    "Washington Wizards": "was",
}

ESPN_LOGO_URL = "https://a.espncdn.com/i/teamlogos/nba/500/scoreboard/{abbrev}.png"


def http_get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGO_DIR, exist_ok=True)


def download_logo(team_name: str) -> str:
    """Download team logo to assets folder; return local path or empty string."""
    abbr = TEAM_ABBR.get(team_name)
    if not abbr:
        return ""
    dest = os.path.join(LOGO_DIR, f"{abbr}.png")
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    url = ESPN_LOGO_URL.format(abbrev=abbr)
    try:
        data = http_get(url)
        with open(dest, "wb") as f:
            f.write(data)
        return dest
    except Exception as e:
        print(f"[warn] failed downloading logo for {team_name} -> {url}: {e}")
        return ""


def normalize_event(ev: Dict[str, Any]) -> Dict[str, Any]:
    """Transform API event to a compact site-friendly record."""
    # The Odds API returns bookmaker arrays. We'll capture best prices for h2h and spreads.
    home = ev.get("home_team")
    away = ev.get("away_team")
    commence = ev.get("commence_time")  # ISO timestamp in UTC

    best_h2h: Dict[str, Any] = {"home": None, "away": None}
    best_spread: Dict[str, Any] = {"home": None, "away": None}

    for bk in ev.get("bookmakers", []):
        for market in bk.get("markets", []):
            if market.get("key") == "h2h":
                for outcome in market.get("outcomes", []):
                    if outcome.get("name") == home:
                        price = outcome.get("price")
                        if price is not None:
                            best_h2h["home"] = max(best_h2h["home"] or price, price)
                    elif outcome.get("name") == away:
                        price = outcome.get("price")
                        if price is not None:
                            best_h2h["away"] = max(best_h2h["away"] or price, price)
            elif market.get("key") == "spreads":
                for outcome in market.get("outcomes", []):
                    entry = {
                        "point": outcome.get("point"),
                        "price": outcome.get("price"),
                    }
                    if outcome.get("name") == home:
                        best_spread["home"] = entry
                    elif outcome.get("name") == away:
                        best_spread["away"] = entry

    # Download logos opportunistically
    home_logo = download_logo(home or "")
    away_logo = download_logo(away or "")

    return {
        "id": ev.get("id"),
        "sport_key": ev.get("sport_key"),
        "commence_time": commence,
        "home_team": home,
        "away_team": away,
        "logos": {"home": os.path.relpath(home_logo, ROOT) if home_logo else "", "away": os.path.relpath(away_logo, ROOT) if away_logo else ""},
        "best_h2h": best_h2h,
        "best_spread": best_spread,
        "bookmakers_count": len(ev.get("bookmakers", [])),
    }


def filter_today_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return events that start on current day in local time."""
    # Consider local date of commence_time
    today_local = dt.datetime.now().date()
    out: List[Dict[str, Any]] = []
    for ev in events:
        ct = ev.get("commence_time")
        try:
            # Example: 2025-12-05T01:00:00Z
            dt_utc = dt.datetime.fromisoformat(ct.replace("Z", "+00:00"))
        except Exception:
            continue
        local = dt_utc.astimezone().date()
        if local == today_local:
            out.append(ev)
    return out


def main():
    ensure_dirs()
    print("Fetching NBA odds...")
    raw_bytes = http_get(API_URL)
    payload = json.loads(raw_bytes)
    # Filter to today and normalize
    today_events = filter_today_events(payload)
    normalized = [normalize_event(ev) for ev in today_events]

    stamp = dt.datetime.now().strftime("%Y-%m-%d")
    out_latest = os.path.join(DATA_DIR, "latest.json")
    out_dated = os.path.join(DATA_DIR, f"odds_{stamp}.json")

    meta = {
        "generated_at": dt.datetime.now().isoformat(),
        "source": "the-odds-api",
        "count": len(normalized),
    }

    out_obj = {"meta": meta, "events": normalized}

    with open(out_latest, "w") as f:
        json.dump(out_obj, f, indent=2)
    with open(out_dated, "w") as f:
        json.dump(out_obj, f, indent=2)

    print(f"Wrote {len(normalized)} events to:\n - {out_latest}\n - {out_dated}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {e}")
        sys.exit(1)
