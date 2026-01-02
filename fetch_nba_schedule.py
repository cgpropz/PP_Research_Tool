import requests
import json

API_URL = "https://api.props.cash/nba/schedule"
OUTPUT_FILE = "nba_schedule.json"
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjF0dUkybDZSQjBjWlF2MHM1M28yNSJ9.eyJzdWJzY3JpcHRpb24iOiJwcm8iLCJpc3MiOiJodHRwczovL3Byb3BzLWhlbHBlci51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDc0MjU1MTA0NDAyMTQ2OTc2NzgiLCJhdWQiOlsiaHR0cHM6Ly9wcm9wcy1kb3QtY2FzaC9hcGkiLCJodHRwczovL3Byb3BzLWhlbHBlci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzY1ODI5NjI3LCJleHAiOjE3Njg0MjE2MjcsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJhenAiOiJrSTc2UFlrOUEzZzd5VXR5aFkzQWhLbXI5b3ZpSEF6dyJ9.f2QLyPDiCr6GLVZOPZs_meFPdgviJHixHjb9gLSfXPIT2E2aniB-OXKsmMeSOi6qSfyNmDaOlbLt1h1f7vTNlnTHubciMD3bwUtOqfDQMTof2AlGyJE2FXb3lqSKGXts5cDC-kW2zga1gZ3VsVtGqHj_WedV5NWQaOlKvEjdu8TfPL7HydkABm-TovoWMlANxXQgrInHSMmubvUKNaA8xv4wLGM0jj0kf3xSe2ag6qYPVf6fsdV4pRmvLygYy1WiwolLs6KBxHML_WwAn81AObsipWPy8BFSZAN1w96Frgm0FFF0RvGEJdjFU1lWf6RRNf3VrcWPfwS5NdrKGS8oiw",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; NBAResearchBot/1.0)"
}

def fetch_and_save_schedule():
    response = requests.get(API_URL, headers=HEADERS)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
        print(f"Response content: {response.text}")
        return
    data = response.json()
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Schedule data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_and_save_schedule()
