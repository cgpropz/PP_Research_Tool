from seleniumbase import Driver
import pandas as pd
import sys
import traceback

url = 'https://www.nba.com/stats/players/boxscores'

driver = Driver(uc=True, headless=True)
try:
    driver.get(url)
    driver.sleep(5)

    # Try multiple selectors in order of preference.
    # 1) Exact Crom class observed
    # 2) Any class that starts with Crom_table (more resilient to suffix changes)
    # 3) Table that contains a TH with text "PLAYER" (case-insensitive) — most robust
    selectors = [
        ('css selector', 'table.Crom_table__p1iZz'),
        ('css selector', 'table[class^="Crom_table"]'),
        # Case-insensitive XPath: looks for a table containing a TH whose text contains "PLAYER"
        ('xpath', '//table[.//th[contains(translate(normalize-space(.), "abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), "PLAYER")]]'),
    ]

    table = None
    for kind, sel in selectors:
        try:
            print(f"Trying selector: {kind} -> {sel}")
            # longer timeout because the table is rendered asynchronously
            driver.wait_for_element(kind, sel, timeout=30)
            table = driver.find_element(kind, sel)
            print(f"Found table using selector: {sel}")
            break
        except Exception as e:
            print(f"Selector failed: {sel} ({e})")
            # continue to next selector

    if table is None:
        raise RuntimeError("Unable to find the boxscores table on the page with any selector.")

    # Pull HTML and parse with pandas
    df = pd.read_html(table.get_attribute('outerHTML'))[0]
    df.to_csv('Full_Gamelogs25.csv', index=False)
    print("FULL GAMELOGS Data Saved...")
    print(df)

except Exception as exc:
    # Print full traceback for debugging in CI logs
    print("ERROR during Gamelogs scrape:", file=sys.stderr)
    traceback.print_exc()
    # Ensure driver is closed, then re-raise to let the caller/fallback handle it
    try:
        driver.quit()
    except Exception:
        pass
    # Exit non-zero so the workflow can trigger your existing backup fallback
    sys.exit(2)
finally:
    try:
        driver.quit()
    except Exception:
        pass
