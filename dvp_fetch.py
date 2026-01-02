import json
import numpy as np

# Load your DVP_2025.json
with open('DVP_2025.json', 'r') as f:
    dvp = json.load(f)

positions = ['PG', 'SG', 'SF', 'PF', 'C']
stats = ['pts', 'reb', 'ast', 'stl', 'blk', 'to', '3pm', 'fd']

result = {}

for pos in positions:
    # Gather all values for each stat for this position
    stat_values = {stat: [] for stat in stats}
    for team in dvp:
        if pos in dvp[team]:
            for stat in stats:
                val = float(dvp[team][pos].get(stat, 0))
                stat_values[stat].append(val)
    # Calculate league averages
    league_avg = {stat: np.mean(vals) for stat, vals in stat_values.items()}
    # Calculate weighted scores and ranks
    pos_result = {}
    for team in dvp:
        if pos in dvp[team]:
            team_stats = {}
            for stat in stats:
                val = float(dvp[team][pos].get(stat, 0))
                avg = league_avg[stat] if league_avg[stat] else 1
                score = float(f"{(val / avg) if avg else 0.0:.2f}")
                team_stats[stat] = {"score": score}
            pos_result[team] = team_stats
    # Add combo stats for each team/position
    for team in pos_result:
        s = pos_result[team]
        pts = s.get('pts', {}).get('score', 0.0)
        reb = s.get('reb', {}).get('score', 0.0)
        ast = s.get('ast', {}).get('score', 0.0)
        # Combos: average the component scores
        s['pra'] = {'score': float(f"{(pts + reb + ast) / 3:.2f}")}
        s['pr']  = {'score': float(f"{(pts + reb) / 2:.2f}")}
        s['pa']  = {'score': float(f"{(pts + ast) / 2:.2f}")}
        s['ra']  = {'score': float(f"{(reb + ast) / 2:.2f}")}
    # Add ranks for all stats and combos
    combo_stats = ['pra', 'pr', 'pa', 'ra']
    for stat in stats + combo_stats:
        team_scores = [(team, pos_result[team][stat]['score']) for team in pos_result]
        # Sort ascending so lower scores (tougher defenses) get rank 1
        team_scores.sort(key=lambda x: x[1])
        for rank, (team, _) in enumerate(team_scores, 1):
            pos_result[team][stat]['rank'] = rank
    result[pos] = pos_result

with open('DVP_2025_weighted.json', 'w') as f:
    json.dump(result, f, indent=2)

print('Weighted DVP JSON with combos and ranks saved as DVP_2025_weighted.json')