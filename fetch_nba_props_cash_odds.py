import requests
import json

def fetch_nba_props_cash_odds():
    url = "https://api.props.cash/nba/lines"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; OddsFetcher/1.0)",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjF0dUkybDZSQjBjWlF2MHM1M28yNSJ9.eyJzdWJzY3JpcHRpb24iOiJwcm8iLCJpc3MiOiJodHRwczovL3Byb3BzLWhlbHBlci51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDc0MjU1MTA0NDAyMTQ2OTc2NzgiLCJhdWQiOlsiaHR0cHM6Ly9wcm9wcy1kb3QtY2FzaC9hcGkiLCJodHRwczovL3Byb3BzLWhlbHBlci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzY1ODI5NjI3LCJleHAiOjE3Njg0MjE2MjcsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJhenAiOiJrSTc2UFlrOUEzZzd5VXR5aFkzQWhLbXI5b3ZpSEF6dyJ9.f2QLyPDiCr6GLVZOPZs_meFPdgviJHixHjb9gLSfXPIT2E2aniB-OXKsmMeSOi6qSfyNmDaOlbLt1h1f7vTNlnTHubciMD3bwUtOqfDQMTof2AlGyJE2FXb3lqSKGXts5cDC-kW2zga1gZ3VsVtGqHj_WedV5NWQaOlKvEjdu8TfPL7HydkABm-TovoWMlANxXQgrInHSMmubvUKNaA8xv4wLGM0jj0kf3xSe2ag6qYPVf6fsdV4pRmvLygYy1WiwolLs6KBxHML_WwAn81AObsipWPy8BFSZAN1w96Frgm0FFF0RvGEJdjFU1lWf6RRNf3VrcWPfwS5NdrKGS8oiw"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    with open("nba_player_odds.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("NBA player prop odds saved to nba_player_odds.json")


def run():
    fetch_nba_props_cash_odds()

if __name__ == "__main__":
    run()
