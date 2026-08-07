import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By

def run_test():
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Enable performance logging to capture network requests
    options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Edge(options=options)

    try:
        print("--- Step 1: Navigating to Month=3 Year=2026 ---")
        driver.get("https://impds.nic.in/sale/stateUnautmated?month=3&year=2026")
        time.sleep(2)

        print("--- Step 2: Navigating to Goa state page via stateData('30') ---")
        driver.execute_script("stateData('30');")
        time.sleep(3)

        print("--- Step 3: Navigating to North Goa (585) district ---")
        driver.execute_script("stateData('585');")
        time.sleep(3)

        print("--- Step 4: Opening Live FPS list via liveFpsdata('30', '585') ---")
        driver.execute_script("liveFpsdata('30', '585');")
        time.sleep(3)

        with open("./fps_list_modal.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("--- Step 5: Checking FPS items in modal ---")
        fps_links = driver.find_elements(By.XPATH, "//div[@id='liveDivId']//a[contains(@onclick, 'stateData')]")
        print(f"Found {len(fps_links)} FPS links in modal")
        if fps_links:
            first_fps = fps_links[0]
            print("First FPS text:", first_fps.text)
            print("First FPS onclick:", first_fps.get_attribute("onclick"))
            
            # Clear performance logs
            driver.get_log("performance")
            
            # Click first FPS link
            driver.execute_script("arguments[0].click();", first_fps)
            time.sleep(3)
            
            # Check performance logs for AJAX requests
            logs = driver.get_log("performance")
            print("\n--- Network Requests after clicking FPS ---")
            for entry in logs:
                log_msg = json.loads(entry["message"])["message"]
                if log_msg["method"] == "Network.requestWillBeSent":
                    url = log_msg["params"]["request"]["url"]
                    if "sale" in url or "Ajax" in url or "impds" in url:
                        print("REQUEST:", url)

            with open("./fps_clicked_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            driver.save_screenshot("./fps_clicked.png")
            print("Saved fps_clicked_page.html and screenshot")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
