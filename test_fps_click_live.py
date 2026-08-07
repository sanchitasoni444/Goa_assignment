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
    
    driver = webdriver.Edge(options=options)

    try:
        print("--- Step 1: Navigating to Month=3 Year=2026 ---")
        driver.get("https://impds.nic.in/sale/stateUnautmated?month=3&year=2026")
        time.sleep(2)

        print("--- Step 2: Navigating to Goa state page via stateData('30') ---")
        driver.execute_script("stateData('30');")
        time.sleep(2)

        print("--- Step 3: Navigating to North Goa (585) district ---")
        driver.execute_script("stateData('585');")
        time.sleep(2)

        print("--- Step 4: Opening Live FPS list via liveFpsdata('30', '585') ---")
        driver.execute_script("liveFpsdata('30', '585');")
        time.sleep(2)

        print("--- Step 5: Executing stateData('158500200184') for first FPS ---")
        driver.execute_script("stateData('158500200184');")
        time.sleep(3)

        with open("./fps_158500200184_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("./fps_158500200184.png")

        print("Saved HTML and screenshot for FPS 158500200184!")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        print("\n--- Summary cards on FPS page ---")
        for card in soup.find_all(class_=["card", "info-box", "metro-nav-block", "state_count", "custom-metro"]):
            print(card.get_text(separator=' ', strip=True)[:100])

        print("\n--- All tables on FPS page ---")
        for i, tbl in enumerate(soup.find_all("table")):
            print(f"Table {i}:")
            for tr in tbl.find_all("tr"):
                print("  ", [td.get_text(strip=True) for td in tr.find_all(["th", "td"])])

        print("\n--- Plus (+) / Expand toggles for Coarse Grains ---")
        for btn in soup.find_all(class_=["activator", "toggle", "menu-toggle", "fa-plus", "fa-plus-circle", "fa-angle-down", "expand"]):
            print(f"<{btn.name} class='{btn.get('class')}' onclick='{btn.get('onclick')}'>{btn.text.strip()}</{btn.name}>")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
