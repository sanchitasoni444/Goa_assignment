import os
import json
import pandas as pd
from pathlib import Path
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MONTHS_TO_SCRAPE = [("3", "2026"), ("4", "2026")]
DISTRICTS = {"585": "north_goa", "586": "south_goa"}
STATE_CODE = "30"

def get_edge_driver():
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Edge(options=options)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_fps_data(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {
        "summary": {},
        "tables": {}
    }
    
    blocks = soup.find_all("div", class_="metro-nav-block1")
    for block in blocks:
        status_div = block.find("div", class_="status1")
        counter_span = block.find("span", class_="counter")
        if status_div and counter_span:
            key = status_div.get_text(separator=' ', strip=True).split('<!--')[0].strip()
            val = counter_span.get_text(strip=True)
            if key and val:
                data["summary"][key] = val

    tables = soup.find_all("table")
    for tbl in tables:
        headers = [th.get_text(strip=True) for th in tbl.find_all("th")]
        header_text = " ".join(headers).lower()
        
        table_data = []
        for tr in tbl.find_all("tr"):
            row = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
            if row:
                table_data.append(row)

        if "number of transactions" in header_text or "total transaction" in header_text:
            data["tables"]["Number of Transactions"] = table_data
        elif "number of transacted ration cards" in header_text or "ration card table" in header_text or "ration card" in header_text:
            data["tables"]["Number of Transacted Ration Cards"] = table_data
        elif "distributed quantity" in header_text:
            data["tables"]["Distributed Quantity"] = table_data
            
    return data

def scrape_fps_list(driver, month, year, district_code, district_name):
    output_dir = f"data/raw/{year}_{month.zfill(2)}/{district_name}"
    ensure_dir(output_dir)
    wait = WebDriverWait(driver, 15)

    try:
        logger.info(f"Navigating to Homepage")
        driver.get("https://impds.nic.in/sale/")

        modal_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#calModal a")))
        driver.execute_script("arguments[0].click();", modal_btn)

        year_select_elem = wait.until(EC.presence_of_element_located((By.ID, "selectedyear")))
        year_select = Select(year_select_elem)
        year_select.select_by_value(year)

        month_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@onclick, 'OnorcStateWisePage({int(month)})')]")))
        driver.execute_script("arguments[0].click();", month_btn)

        states_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@onclick, 'liveStatesdata') or contains(@class, 'card')]//a[contains(@onclick, 'liveStatesdata')] | //a[contains(@onclick, 'liveStatesdata')] | //div[contains(@onclick, 'liveStatesdata')]")))
        driver.execute_script("arguments[0].click();", states_btn)

        goa_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, \"stateData('30')\")]")))
        driver.execute_script("arguments[0].click();", goa_btn)

        dist_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@onclick, \"stateData('{district_code}')\")]")))
        driver.execute_script("arguments[0].click();", dist_btn)

        fps_list_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@onclick, 'liveFpsdata')] | //div[contains(@onclick, 'liveFpsdata')]")))
        driver.execute_script("arguments[0].click();", fps_list_btn)

        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='stateDivId']//a[contains(@onclick, 'stateData')] | //div[@id='liveDivId']//a[contains(@onclick, 'stateData')]")))

        fps_links = driver.find_elements(By.XPATH, "//div[@id='stateDivId']//a[contains(@onclick, 'stateData')] | //div[@id='liveDivId']//a[contains(@onclick, 'stateData')]")
        fps_ids = []
        for link in fps_links:
            onclick = link.get_attribute("onclick")
            if "stateData" in onclick:
                f_id = onclick.split("'")[1]
                f_name = link.text.strip().replace(" ", "_").replace("/", "_").replace(":", "_")
                fps_ids.append((f_id, f_name))

        logger.info(f"Found {len(fps_ids)} FPS in {district_name}")

        for fps_id, fps_name in fps_ids:
            file_path = os.path.join(output_dir, f"{fps_id}_{fps_name}.json")
            if os.path.exists(file_path):
                logger.info(f"Skipping {fps_id}, file already exists.")
                continue

            success = False
            for attempt in range(3):
                try:
                    logger.info(f"Processing FPS {fps_id} (Attempt {attempt + 1}/3)")
                    driver.execute_script(f"stateData('{fps_id}');")
                    
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "metro-nav-block1")))
                    
                    import time
                    time.sleep(1) # Tiny sleep to ensure chart rendering doesn't shift the DOM dynamically
                    
                    try:
                        expand_btns = driver.find_elements(By.CSS_SELECTOR, ".activator, .menu-toggle, .fa-plus, .fa-plus-circle")
                        for btn in expand_btns:
                            if btn.is_displayed():
                                driver.execute_script("arguments[0].click();", btn)
                    except Exception:
                        pass 

                    data = extract_fps_data(driver)
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                        
                    success = True
                    break
                except Exception as e:
                    logger.error(f"Error extracting FPS {fps_id}: {e}")
                    driver.execute_script(f"liveFpsdata('30', '{district_code}');")
                    import time
                    time.sleep(3)

            if not success:
                logger.error(f"Failed to extract FPS {fps_id} after 3 attempts.")
                
    except Exception as e:
        logger.error(f"Error in district {district_name}: {e}")

def main():
    driver = get_edge_driver()
    try:
        for month, year in MONTHS_TO_SCRAPE:
            for d_code, d_name in DISTRICTS.items():
                logger.info(f"Starting scraping for {d_name} ({year}-{month.zfill(2)})")
                scrape_fps_list(driver, month, year, d_code, d_name)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
