import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

url = "https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php"
pos = ['PG', 'SG', 'SF', 'PF', 'C']

def getColumnNames(table):
    return [th.text.strip() for th in table.find("tr").find_all("th")]

def genDf(table, column_names, pos):
    data = []
    cl = "GC-30" + " " + pos
    for tr in table.find_all("tr", class_=[cl]):
        row_data = [td.text.strip() for td in tr.find_all("td")]
        team_column = tr.find("td", class_="left team-cell")
        if team_column:
            team_text = team_column.text.strip()
            team_code = team_text[:3]
            if team_code == 'NOR':
                team_code = 'NOP'
            team_name = team_text[3:]
            row_data = [team_code, team_name] + row_data
        data.append(row_data)
    df = pd.DataFrame(data, columns=["tsc", "team_name"] + column_names)
    df = df.drop("Team", axis=1, errors="ignore")
    df['tsc'] = df['tsc'].str.upper().replace({'UTH': 'UTA'})
    return df

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
table = soup.find("table", {"id": "data-table"})
column_names = getColumnNames(table)
final_df = pd.DataFrame()

for p in pos:
    df = genDf(table, column_names, p)
    if not df.empty:
        df.columns = df.columns.str.lower()
        df.insert(0, 'pos', p)
        final_df = pd.concat([final_df, df], ignore_index=True)

# Save to CSV (optional)
final_df.to_csv('DVP_2025.csv', index=False)

# Convert to nested JSON: {team: {pos: {stat: value, ...}}}
dvp_json = {}
for _, row in final_df.iterrows():
    team = row['tsc']
    position = row['pos']
    if team not in dvp_json:
        dvp_json[team] = {}
    dvp_json[team][position] = {col: row[col] for col in final_df.columns if col not in ['tsc', 'team_name', 'pos']}

with open('DVP_2025.json', 'w') as f:
    json.dump(dvp_json, f, indent=2)

print('DVP Data Saved as JSON...')