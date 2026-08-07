import requests
from bs4 import BeautifulSoup

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. Set Month=3 Year=2026
session.get("https://impds.nic.in/sale/stateUnautmated?month=3&year=2026", headers=headers)

# 2. Call districtByCountryAjax with fps_id 158500200184
fps_id = "158500200184"
print(f"--- Requesting districtByCountryAjax?stateCode={fps_id} ---")
resp_fps_data = session.get(f"https://impds.nic.in/sale/districtByCountryAjax?stateCode={fps_id}", headers=headers)
print("status:", resp_fps_data.status_code)

soup = BeautifulSoup(resp_fps_data.text, "html.parser")
with open("./fps_detail_ajax.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())

print("Saved fps_detail_ajax.html")

print("\n--- Summary cards / text ---")
for card in soup.find_all(class_=["card", "info-box", "metro-nav-block", "state_count", "custom-metro"]):
    print(card.get_text(separator=' ', strip=True)[:100])

print("\n--- All tables found ---")
for i, tbl in enumerate(soup.find_all("table")):
    print(f"Table {i}:")
    for tr in tbl.find_all("tr"):
        print("  ", [td.get_text(strip=True) for td in tr.find_all(["th", "td"])])
