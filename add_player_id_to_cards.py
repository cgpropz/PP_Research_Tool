import json

# Load players.json and build a name->id map
with open('players.json', 'r') as f:
    players = json.load(f)
name_to_id = {}
for p in players:
    # Try both 'name' and 'full_name' keys, fallback to None
    name = p.get('name') or p.get('full_name')
    if name:
        name_to_id[name.strip().lower()] = p['id']

# Helper to match player name

def get_player_id(name):
    if not name:
        return None
    return name_to_id.get(name.strip().lower())

# Update a file with player_id

def update_file(path):
    with open(path, 'r') as f:
        data = json.load(f)
    for obj in data:
        pid = get_player_id(obj.get('name'))
        if pid:
            obj['player_id'] = pid
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

update_file('PLAYER_UI_CARDS_PERFECT.json')
update_file('PLAYER_UI_CARDS_PERFECT.json')
print('Done: player_id added to both files.')
