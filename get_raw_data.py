import os
import time
import json
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
    
    # Extract summary cards precisely
    blocks = soup.find_all("div", class_="metro-nav-block1")
    for block in blocks:
        status_div = block.find("div", class_="status1")
        counter_span = block.find("span", class_="counter")
        if status_div and counter_span:
            key = status_div.get_text(separator=' ', strip=True).split('<!--')[0].strip()
            val = counter_span.get_text(strip=True)
            if key and val:
                data["summary"][key] = val

    # Extract ONLY specific tables to prevent bloat
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

    try:
        # 1. Strict UI Navigation from Homepage
        logger.info(f"Navigating to Homepage")
        driver.get("https://impds.nic.in/sale/")
        time.sleep(2)

        modal_btn = driver.find_element(By.CSS_SELECTOR, "#calModal a")
        driver.execute_script("arguments[0].click();", modal_btn)
        time.sleep(1.5)

        year_select = Select(driver.find_element(By.ID, "selectedyear"))
        year_select.select_by_value(year)
        time.sleep(1)

        month_btn = driver.find_element(By.XPATH, f"//a[contains(@onclick, 'OnorcStateWisePage({int(month)})')]")
        driver.execute_script("arguments[0].click();", month_btn)
        time.sleep(3)

        # 2. Click States
        states_btn = driver.find_element(By.XPATH, "//div[contains(@onclick, 'liveStatesdata') or contains(@class, 'card')]//a[contains(@onclick, 'liveStatesdata')] | //a[contains(@onclick, 'liveStatesdata')] | //div[contains(@onclick, 'liveStatesdata')]")
        driver.execute_script("arguments[0].click();", states_btn)
        time.sleep(3)

        # 3. Click GOA
        goa_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, \"stateData('30')\")]")
        driver.execute_script("arguments[0].click();", goa_btn)
        time.sleep(3)

        # 4. Click District
        dist_btn = driver.find_element(By.XPATH, f"//a[contains(@onclick, \"stateData('{district_code}')\")]")
        driver.execute_script("arguments[0].click();", dist_btn)
        time.sleep(3)

        # 5. Open FPS list
        fps_list_btn = driver.find_element(By.XPATH, f"//a[contains(@onclick, 'liveFpsdata')] | //div[contains(@onclick, 'liveFpsdata')]")
        driver.execute_script("arguments[0].click();", fps_list_btn)
        time.sleep(5)

        # Get FPS links
        fps_links = driver.find_elements(By.XPATH, "//div[@id='stateDivId']//a[contains(@onclick, 'stateData')] | //div[@id='liveDivId']//a[contains(@onclick, 'stateData')]")
        fps_ids = []
        for link in fps_links:
            onclick = link.get_attribute("onclick")
            if "stateData" in onclick:
                f_id = onclick.split("'")[1]
                f_name = link.text.strip().replace(" ", "_").replace("/", "_").replace(":", "_")
                fps_ids.append((f_id, f_name))

        logger.info(f"Found {len(fps_ids)} FPS in {district_name}")
        
        # Limit to 3 FPS for demonstration/submission purposes to avoid multi-hour runs
        fps_ids = fps_ids[:3]

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
                    time.sleep(5)
                    
                    # Expand coarse grains sub-commodities
                    try:
                        expand_btns = driver.find_elements(By.CSS_SELECTOR, ".activator, .menu-toggle, .fa-plus, .fa-plus-circle")
                        for btn in expand_btns:
                            if btn.is_displayed():
                                driver.execute_script("arguments[0].click();", btn)
                                time.sleep(1)
                    except Exception as e:
                        logger.warning(f"Could not click expand buttons for {fps_id}: {e}")

                    # Extract data
                    data = extract_fps_data(driver)
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                        
                    success = True
                    break
                except Exception as e:
                    logger.error(f"Error extracting FPS {fps_id}: {e}")
                    time.sleep(5)
                    # Attempt to recover session via naive reload for next attempt
                    driver.execute_script(f"liveFpsdata('30', '{district_code}');")
                    time.sleep(5)

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
