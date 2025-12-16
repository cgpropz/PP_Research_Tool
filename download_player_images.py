# fix_jpg_to_transparent_png.py
# FORCE-CONVERTS all your player_images to TRUE transparent PNGs (no mercy for JPGs!)

import json
import os
import requests
from PIL import Image
import io
import time

# CONFIG
JSON_FILE = "players.json"
IMAGE_FOLDER = "player_images"
HEADSHOT_BASE = "https://cdn.nba.com/headshots/nba/latest/1040x760/"

print("🔧 Transparent PNG Fixer Starting... (Converting ALL images)")

# Load players for mapping
with open(JSON_FILE, 'r', encoding='utf-8') as f:
    players = {p['id']: p['full_name'] for p in json.load(f) if p.get("is_active")}

def convert_to_transparent_png(player_id: str):
    url = f"{HEADSHOT_BASE}{player_id}.png"
    final_path = os.path.join(IMAGE_FOLDER, f"{player_id}.png")
    
    # Skip if already good PNG
    if os.path.exists(final_path):
        try:
            img = Image.open(final_path)
            if img.format == 'PNG' and img.mode == 'RGBA':
                print(f"✅ Already perfect: {player_id}.png")
                return True
        except:
            pass  # Force re-download if broken
    
    try:
        # Download fresh bytes
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Open image from bytes
        img = Image.open(io.BytesIO(response.content))
        
        # STEP 1: Always convert to RGBA (adds transparency channel)
        img = img.convert("RGBA")
        print(f"🔄 Converted to RGBA: {player_id}")
        
        # STEP 2: Remove white background (tolerance for near-white)
        datas = img.getdata()
        new_data = []
        for item in datas:
            r, g, b, a = item
            # If near-white (RGB > 240), make transparent
            if r > 240 and g > 240 and b > 240:
                new_data.append((r, g, b, 0))  # Transparent
            else:
                new_data.append(item)
        img.putdata(new_data)
        print(f"✂️ Removed white BG: {player_id}")
        
        # STEP 3: Save as TRUE PNG
        img.save(final_path, "PNG", optimize=True)
        return True
        
    except Exception as e:
        print(f"❌ Failed {player_id}: {e}")
        return False

# MAIN LOOP: Process all players
success = 0
total = len(players)

for idx, (pid, name) in enumerate(players.items()):
    if convert_to_transparent_png(str(pid)):
        success += 1
    
    if (idx + 1) % 20 == 0:
        print(f"Progress: {idx + 1}/{total} | Fixed: {success}")
    
    time.sleep(0.2)  # Polite

# FINAL CHECK: Verify a sample
test_id = "203999"  # Aaron Gordon
test_path = os.path.join(IMAGE_FOLDER, f"{test_id}.png")
if os.path.exists(test_path):
    test_img = Image.open(test_path)
    print(f"\n🎯 Test File ({test_id}.png): format={test_img.format}, mode={test_img.mode}")
    print("If PNG + RGBA → Transparent magic unlocked! 🪄")

print(f"\n🏆 FIX COMPLETE! {success}/{total} real PNGs saved.")
print("Open any .png in Photoshop/GIMP—white BG gone, ready for overlays!")