from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import sys

def current_nba_season_str(today=None):
    if today is None:
        today = datetime.now()
    year = today.year
    if today.month >= 10:
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year
    return f"{start_year}-{str(end_year)[-2:]}"

nba_season = current_nba_season_str()
today_str = datetime.now().strftime("%m/%d/%Y")
nba_url = f"https://www.nba.com/stats/players/boxscores/?Season={nba_season}&SeasonType=Regular%20Season"

def get_boxscores_table(page, timeout=120):
    selector = 'table[class^="Crom_table"]'
    page.wait_for_selector(selector, timeout=timeout * 1000)
    table = page.query_selector(selector)
    if not table:
        return None
    return table.evaluate('node => node.outerHTML')

def main():
    print(f"Detected NBA season: {nba_season} • Scraping up to {today_str}")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # Stay headless, but maximize stealth
            args=["--disable-blink-features=AutomationControlled"]
        )

        # Enhanced context options for stealth
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", # Latest Chrome UA
            locale="en-US",
            timezone_id="America/New_York",
            device_scale_factor=1.0,
            permissions=["geolocation"],
            geolocation={"longitude": -73.935242, "latitude": 40.73061}, # New York
        )

        # Set extra HTTP headers for page requests
        context.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nba.com/",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
        })

        page = context.new_page()

        print(f"Loading {nba_url} ...")
        page.goto(nba_url, timeout=180000)
        page.wait_for_timeout(12000)

        # Accept cookie/privacy banner if present
        for btn_word in ["accept", "agree", "consent"]:
            try:
                button = page.query_selector(f'button:has-text("{btn_word}")')
                if button:
                    button.click()
                    print(f"Clicked '{btn_word}' button.")
                    page.wait_for_timeout(2500)
                    break
            except Exception:
                pass

        page.wait_for_timeout(6000)
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(3000)

        # Debug: List all table class names found on the page
        print("All tables on page:")
        for t in page.query_selector_all("table"):
            print("Table class:", t.get_attribute("class"))

        try:
            table_html = get_boxscores_table(page, timeout=120)
            if not table_html:
                print("ERROR: Could not find NBA boxscores table.", file=sys.stderr)
                # Print an HTML snippet for debugging
                print("DEBUG: Dumping first 10,000 chars of page HTML:")
                print(page.content()[:10000])
                browser.close()
                sys.exit(2)
            df = pd.read_html(table_html)[0]
        except Exception as e:
            print("ERROR locating/parsing the NBA boxscores table.", file=sys.stderr)
            print(e, file=sys.stderr)
            print("DEBUG: Dumping first 10,000 chars of page HTML:")
            print(page.content()[:10000])
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
    
