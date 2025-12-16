import os
import json
from string import Template

# Paths
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../PLAYER_UI_CARDS_PERFECT.json'))
TEMPLATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../players-props/player-template.html'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../players-props/'))

# Load player data
with open(DATA_PATH, 'r') as f:
    players = json.load(f)

# Get unique player slugs and names
unique_players = {}
for p in players:
    import unicodedata
    def slugify(name):
        # Normalize and remove diacritics
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        name = name.lower().replace(' ', '-').replace("'", '').replace('.', '')
        name = ''.join(c for c in name if c.isalnum() or c == '-')
        name = name.strip('-')
        return name
    if 'name' in p and p['name']:
        slug = slugify(p['name'])
        if slug not in unique_players:
            unique_players[slug] = p['name']

# Read template
with open(TEMPLATE_PATH, 'r') as f:
    template_html = f.read()

# Generate a static page for each player
for slug, name in unique_players.items():
    out_path = os.path.join(OUTPUT_DIR, f'{slug}.html')
    # The template is dynamic, so just copy it for each player (JS will load correct data by slug)
    with open(out_path, 'w') as out:
        out.write(template_html)

print(f"Generated {len(unique_players)} player pages in {OUTPUT_DIR}")
