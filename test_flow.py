import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def run_test():
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Edge(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        print("--- Step 1: Navigating to impds.nic.in/sale/ ---")
        driver.get("https://impds.nic.in/sale/")
        time.sleep(2)

        print("--- Step 2: Selecting Year 2026 and Month March (3) ---")
        # Click month-year button in top navbar to open modal
        month_nav_btn = driver.find_element(By.XPATH, "//a[contains(@data-target, '#myModal10') or contains(text(), '2026') or contains(text(), '2025')]")
        month_nav_btn.click()
        time.sleep(1)

        # Select 2026 in dropdown #selectedyear
        year_select = Select(driver.find_element(By.ID, "selectedyear"))
        year_select.select_by_value("2026")
        time.sleep(1)

        # Click Mar (Month 3) button
        mar_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, 'OnorcStateWisePage(3)') or contains(@onclick, 'OnorcStateWisePage(03)')]")
        mar_btn.click()
        time.sleep(3)

        print("Current URL after Month selection:", driver.current_url)

        print("--- Step 3: Clicking States summary card / liveStatesdata ---")
        # Find States card or button with liveStatesdata
        try:
            states_card = driver.find_element(By.XPATH, "//*[@onclick='liveStatesdata()']")
            driver.execute_script("arguments[0].scrollIntoView(true);", states_card)
            states_card.click()
        except Exception as e:
            print("Direct click failed, executing script liveStatesdata():", e)
            driver.execute_script("liveStatesdata();")

        time.sleep(3)

        # Wait for modal or liveDivId
        soup = BeautifulSoup(driver.page_source, "html.parser")
        live_div = soup.find(id="liveDivId")
        if live_div:
            print("Live States Content Length:", len(live_div.get_text()))
            # Save snippet of liveDivId
            with open("./live_states.html", "w", encoding="utf-8") as f:
                f.write(str(live_div))
        
        print("--- Step 4: Clicking GOA ---")
        goa_link = driver.find_element(By.XPATH, "//a[contains(@onclick, \"stateData('30')\") or contains(text(), 'GOA') or contains(text(), 'Goa')]")
        driver.execute_script("arguments[0].click();", goa_link)
        time.sleep(3)

        print("Current URL after Goa click:", driver.current_url)
        with open("./goa_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("--- Step 5: Looking for Districts card / District modal ---")
        soup_goa = BeautifulSoup(driver.page_source, "html.parser")
        print("Goa page text snippet:")
        print(soup_goa.get_text(separator=' ', strip=True)[:500])

        # Save screenshot
        driver.save_screenshot("./goa_page.png")
        print("Saved goa_page.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
