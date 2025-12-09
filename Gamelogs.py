from seleniumbase import Driver
import pandas as pd
import time  # For retries

# Retry decorator (auto-retries 3x with backoff)
def retry_on_exception(max_attempts=3, backoff=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e  # Final fail → raise
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {backoff**attempt}s...")
                    time.sleep(backoff ** attempt)
            return None
        return wrapper
    return decorator

url = 'https://www.nba.com/stats/players/boxscores'

@retry_on_exception(max_attempts=3, backoff=2)  # ← Bulletproof retry
def scrape_gamelogs():
    driver = Driver(uc=True, headless=True)  # No timeout here – fixed!
    try:
        driver.set_page_load_timeout(30)  # Global page load timeout (30s)
        driver.get(url)
        driver.sleep(10)  # Initial JS load buffer

        # Wait for table (with built-in SB timeout ~10s, but retry covers flakes)
        table_xpath = '/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table'
        driver.wait_for_element('xpath', table_xpath, timeout=30)  # Per-wait timeout here

        driver.sleep(6)
        driver.wait_for_element('xpath', '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/div/button', timeout=30).click()
        driver.sleep(1)
        driver.wait_for_element('xpath', '/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select', timeout=30).click()
        driver.sleep(1)
        driver.wait_for_element('xpath', '/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select/option[1]', timeout=30).click()
        driver.sleep(2)

        # Scroll for lazy-load
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        driver.sleep(10)  # Post-scroll settle

        # Grab table
        table = driver.find_element('xpath', table_xpath)
        df = pd.read_html(table.get_attribute('outerHTML'))[0]
        df.to_csv('Full_Gamelogs25.csv', index=False)
        print("FULL GAMELOGS Data Saved...")
        print(df.head())  # Debug preview
        return df
    finally:
        driver.quit()

# Run it
print("Running full Gamelogs scrape (undetected-chromedriver)...")
try:
    scrape_gamelogs()
except Exception as e:
    print(f"Gamelogs failed → backup needed: {e}")