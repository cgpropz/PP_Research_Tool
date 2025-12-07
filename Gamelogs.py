from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import sys

# NBA season start and today's date for info only (NBA.com loads all, no filter)
season_start = "10/01/2025"
today = datetime.now().strftime("%m/%d/%Y")
nba_url = "https://www.nba.com/stats/players/boxscores"

def get_boxscores_table(page, timeout=60):
    """
    Wait for the player stats table and return its HTML.
    """
    selector = 'table[class^="Crom_table"]'
    page.wait_for_selector(selector, timeout=timeout * 1000)
    table = page.query_selector(selector)
    if not table:
        return None
    # Get outer HTML for pandas
    return table.evaluate('node => node.outerHTML')

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        print(f"Loading {nba_url} ...")
        page.goto(nba_url, timeout=90000)
        page.wait_for_timeout(8000)

        # Click cookie/privacy modal if present
        for btn_word in ["accept", "agree", "consent"]:
            try:
                button = page.query_selector(f'button:has-text("{btn_word}")')
                if button:
                    button.click()
                    print(f"Clicked '{btn_word}' button.")
                    page.wait_for_timeout(2000)
                    break
            except Exception:
                pass

        page.wait_for_timeout(4000)
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

        try:
            table_html = get_boxscores_table(page)
            if not table_html:
                print("ERROR: Could not find NBA boxscores table.", file=sys.stderr)
                browser.close()
                sys.exit(2)
            df = pd.read_html(table_html)[0]
        except Exception as e:
            print("ERROR locating/parsing the NBA boxscores table.", file=sys.stderr)
            print(e, file=sys.stderr)
            browser.close()
            sys.exit(2)

        csv_file = "Full_Gamelogs25.csv"
        json_file = "Player_Gamelogs25.json"
        try:
            df.to_csv(csv_file, index=False)
            df.to_json(json_file, orient="records")
            print(f"Saved {len(df)} player-game logs to {csv_file} and {json_file}")
            if len(df) > 0:
                print("First game in dataset:")
                print(df.head(1).to_dict(orient="records")[0])
            else:
                print("No player-game logs found!")
        except Exception as e:
            print("ERROR writing output file.", file=sys.stderr)
            print(e, file=sys.stderr)
            browser.close()
            sys.exit(2)
        browser.close()

if __name__ == "__main__":
    main()
