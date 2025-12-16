import json

def add_score_to_cards(path):
    with open(path, 'r') as f:
        data = json.load(f)
    for obj in data:
        # Score = projection / line * 50, if both exist and line > 0
        proj = obj.get('projection')
        line = obj.get('line')
        try:
            proj = float(proj)
            line = float(line)
            if line > 0:
                obj['score'] = round(proj / line * 50, 2)
            else:
                obj['score'] = None
        except (TypeError, ValueError):
            obj['score'] = None
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

add_score_to_cards('PLAYER_UI_CARDS_PERFECT.json')
print('Done: score added to PLAYER_UI_CARDS_PERFECT.json')
