import sys
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By

def test_sel():
    print("Testing Selenium with Edge...")
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Edge(options=options)
    
    print("Navigating to https://impds.nic.in/sale/")
    driver.get("https://impds.nic.in/sale/")
    print("Title:", driver.title)
    
    with open("./impds_edge.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved impds_edge.html successfully!")
    
    driver.quit()

if __name__ == "__main__":
    test_sel()
