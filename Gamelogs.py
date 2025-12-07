import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import time
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

def wait_for_table(driver, timeout=120):
    # Wait for NBA stats table to appear
    selector = "table[class^='Crom_table']"
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element
    except Exception as e:
        print("Timeout or table not found:", e)
        return None

def click_cookie_modal(driver):
    for btn_text in ["accept", "agree", "consent"]:
        try:
            buttons = driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{btn_text}')]")
            for btn in buttons:
                btn.click()
                print(f"Clicked privacy/cookie button: '{btn.text}'")
                time.sleep(2)
                return
        except Exception:
            pass

def main():
    print(f"Detected NBA season: {nba_season} • Scraping up to {today_str}")
    # Launch undetected headless Chrome
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--lang=en-US,en")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # uc takes care of most flags and stealth
    driver = uc.Chrome(options=options)

    try:
        print(f"Loading {nba_url} ...")
        driver.get(nba_url)
        time.sleep(10)

        click_cookie_modal(driver)

        # NBA.com often lazy loads, so scroll down to trigger render
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        table_elem = wait_for_table(driver, timeout=120)
        if not table_elem:
            print("ERROR: NBA boxscores table not found after waiting.")
            # Print a snippet of page HTML for debugging
            print("DEBUG: Dumping first 10,000 chars of page HTML:")
            print(driver.page_source[:10000])
            sys.exit(2)

        table_html = table_elem.get_attribute("outerHTML")
        df = pd.read_html(table_html)[0]

        csv_file = "Full_Gamelogs25.csv"
        json_file = "Player_Gamelogs25.json"
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient="records")

        print(f"Saved {len(df)} player-game logs to {csv_file} and {json_file}")
        if len(df) > 0:
            print("First game in dataset:")
            print(df.head(1).to_dict(orient="records")[0])
        else:
            print("No player-game logs found!")
    except Exception as e:
        print("ERROR scraping NBA.com:", e)
        print("DEBUG: Dumping first 10,000 chars of page HTML:")
        print(driver.page_source[:10000])
        sys.exit(2)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
