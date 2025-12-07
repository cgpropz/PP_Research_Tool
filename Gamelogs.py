from seleniumbase import Driver
import pandas as pd
import sys
import traceback

url = 'https://www.nba.com/stats/players/boxscores'

driver = Driver(uc=True, headless=True)
try:
    driver.get(url)
    driver.sleep(5)

    # Attempt to click any cookie/privacy accept buttons if present
    try:
        buttons = driver.find_elements('css selector', 'button')
        for b in buttons:
            if 'accept' in b.text.lower() or 'agree' in b.text.lower() or 'consent' in b.text.lower():
                print(f"Clicking cookie/privacy button: \"{b.text}\"")
                b.click()
                driver.sleep(2)
                break
    except Exception as e:
        print("No cookie/privacy popup found or error clicking button:", e)

    # Scroll to bottom a couple of times to trigger lazy-load if needed
    for i in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.sleep(2)

    # Try multiple selectors in order of preference.
    # 1) Exact Crom class observed
    # 2) Any class that starts with Crom_table (more resilient to suffix changes)
    # 3) Table that contains a TH with text "PLAYER" (case-insensitive) — most robust
    selectors = [
        ('css selector', 'table.Crom_table__p1iZz'),
        ('css selector', 'table[class^="Crom_table"]'),
        ('xpath', '//table[.//th[contains(translate(normalize-space(.), "abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), "PLAYER")]]'),
    ]

    table = None
    for kind, sel in selectors:
        try:
            print(f"Trying selector: {kind} -> {sel}")
            driver.wait_for_element(kind, sel, timeout=30)
            table = driver.find_element(kind, sel)
            print(f"Found table using selector: {sel}")
            break
        except Exception as e:
            print(f"Selector failed: {sel} ({e})")
            # continue to next selector

    if table is None:
        # Print a snippet of page source for debugging
        print("Unable to find the boxscores table. Dumping first 5000 chars of page source for debug:")
        print(driver.page_source[:5000])
        raise RuntimeError("Unable to find the boxscores table on the page with any selector.")

    # Pull HTML and parse with pandas
    df = pd.read_html(table.get_attribute('outerHTML'))[0]
    df.to_csv('Full_Gamelogs25.csv', index=False)
    print("FULL GAMELOGS Data Saved...")
    print(df)

except Exception as exc:
    print("ERROR during Gamelogs scrape:", file=sys.stderr)
    traceback.print_exc()
    try:
        driver.quit()
    except Exception:
        pass
    sys.exit(2)
finally:
    try:
        driver.quit()
    except Exception:
        pass
