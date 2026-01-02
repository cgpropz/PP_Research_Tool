from seleniumbase import Driver
import pandas as pd
import math
import json

url = 'https://www.nba.com/stats/players/boxscores'

driver = Driver(uc=True, headless=True)
driver.get(url)
driver.sleep(5)

driver.wait_for_element('xpath', '/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table')
driver.sleep(6)

driver.wait_for_element('xpath', '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/div/button').click()
driver.sleep(3)

driver.wait_for_element('xpath', '/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select').click()
driver.sleep(3)

driver.wait_for_element('xpath', '/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select/option[1]').click()
driver.sleep(3)

driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
driver.sleep(5)

table = driver.find_element('xpath','/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table')

df = pd.read_html(table.get_attribute('outerHTML'))[0]
df.to_csv('Full_Gamelogs25.csv', index=False)
print("FULL GAMELOGS Data Saved...")   
print(df.head())

# --- Add this block to always output null instead of NaN in JSON ---
def replace_nan(obj):
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj

# Export to JSON as well
gamelogs = df.to_dict(orient='records')
with open('Player_Gamelogs25.json', 'w') as f:
    json.dump(replace_nan(gamelogs), f, indent=2)
print("JSON gamelogs saved to Player_Gamelogs25.json")