# Player_Gamelogs.py  ← Improved version (no more NaN → null)

import pandas as pd
import json
import numpy as np   # ← we need this!

print("Loading Full_Gamelogs25.csv...")
df = pd.read_csv('Full_Gamelogs25.csv')

print("Cleaning data...")
# Step 1: Replace "-" with real None (NaN in pandas)
df = df.replace('-', None)

# Step 2: Convert percentage columns to float
percent_cols = ['FG%', '3P%', 'FT%']
df[percent_cols] = df[percent_cols].astype(float)

print("Converting to JSON with proper nulls...")
# This is the magic line
player_logs = json.loads(df.to_json(orient='records', force_ascii=False, date_format='iso'))

# Step 5: Save the final CLEAN JSON file
output_file = 'Player_Gamelogs25.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(player_logs, f, indent=2, ensure_ascii=False)

print(f"Done! {len(player_logs):,} player-game logs saved → {output_file}")
print("→ All NaN values are now proper JSON 'null' ")

# Bonus: Show first game as proof
print("\nFirst game in dataset:")
print(json.dumps(player_logs[0], indent=2)[:500] + "...")