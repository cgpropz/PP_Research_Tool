import pandas as pd

url = "https://www.basketball-reference.com/leagues/NBA_2026_per_game.html"

tables = pd.read_html(url)

per_game_stats = tables[0]

# Save to CSV
per_game_stats.to_csv('NBA_2026_Per_Game_Stats.csv', index=False)
print(f"Saved {len(per_game_stats)} player per-game stats to NBA_2026_Per_Game_Stats.csv")
print(per_game_stats.head())  