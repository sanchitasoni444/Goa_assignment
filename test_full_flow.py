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

    try:
        print("--- Step 1: Navigating to impds.nic.in/sale/ ---")
        driver.get("https://impds.nic.in/sale/")
        time.sleep(2)

        print("--- Step 2: Clicking #calModal a to open #myModal10 ---")
        modal_btn = driver.find_element(By.CSS_SELECTOR, "#calModal a")
        driver.execute_script("arguments[0].click();", modal_btn)
        time.sleep(1.5)

        print("--- Selecting Year 2026 ---")
        year_select = Select(driver.find_element(By.ID, "selectedyear"))
        year_select.select_by_value("2026")
        time.sleep(1)

        print("--- Clicking Month Mar (3) ---")
        mar_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, 'OnorcStateWisePage(3)')]")
        driver.execute_script("arguments[0].click();", mar_btn)
        time.sleep(3)

        print("URL after month click:", driver.current_url)

        print("--- Step 3: Triggering liveStatesdata() ---")
        driver.execute_script("liveStatesdata();")
        time.sleep(3)

        print("--- Step 4: Clicking GOA (stateCode 30) ---")
        goa_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, \"stateData('30')\")]")
        driver.execute_script("arguments[0].click();", goa_btn)
        time.sleep(3)

        print("URL after Goa click:", driver.current_url)
        with open("./goa_state_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("--- Step 5: Finding Districts summary card on Goa page ---")
        soup_goa = BeautifulSoup(driver.page_source, "html.parser")
        # Save all onclick and buttons on Goa page
        for tag in soup_goa.find_all(True):
            if tag.get("onclick") or "district" in tag.text.lower():
                print("GOA ELEM:", tag.name, tag.attrs, tag.text.strip()[:60])

    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
