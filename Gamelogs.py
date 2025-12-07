import requests
import pandas as pd
from datetime import datetime

# Set season start and today
season_start = "10/01/2025"
today = datetime.now().strftime("%m/%d/%Y")

url = "https://stats.nba.com/stats/leaguegamelog"
params = {
    "Counter": "1000",
    "DateFrom": season_start,
    "DateTo": today,
    "Direction": "DESC",
    "ISTRound": "",
    "LeagueID": "00",
    "PlayerOrTeam": "P",
    "Season": "2025-26",
    "SeasonType": "Regular Season",
    "Sorter": "DATE"
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com"
}

print(f"Fetching NBA player gamelogs from {season_start} to {today}...")

response = requests.get(url, params=params, headers=headers, timeout=30)
response.raise_for_status()
data = response.json()

columns = data['resultSets'][0]['headers']
rows = data['resultSets'][0]['rowSet']
df = pd.DataFrame(rows, columns=columns)

csv_file = "Full_Gamelogs25.csv"
json_file = "Player_Gamelogs25.json"
df.to_csv(csv_file, index=False)
df.to_json(json_file, orient="records")

print(f"Saved {len(df)} player-game logs to {csv_file} and {json_file}")
if len(df) > 0:
    print("First game in dataset:")
    print(df.head(1).to_dict(orient="records")[0])
else:
    print("No player-game logs found!")
