import requests
from bs4 import BeautifulSoup

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# First set month and year by fetching stateUnautmated
print("--- Requesting stateUnautmated for March 2026 ---")
resp_month = session.get("https://impds.nic.in/sale/stateUnautmated?month=3&year=2026", headers=headers)
print("Month page status:", resp_month.status_code)

print("\n--- Requesting liveDistrictAjax for Goa (stateCode=30) ---")
resp_dist_modal = session.get("https://impds.nic.in/sale/liveDistrictAjax?stateCode=30", headers=headers)
print("liveDistrictAjax status:", resp_dist_modal.status_code)

soup_dist_modal = BeautifulSoup(resp_dist_modal.text, "html.parser")
print("\nDistrict Modal Content:")
print(soup_dist_modal.prettify()[:1000])

for a in soup_dist_modal.find_all("a"):
    print("DIST LINK:", a.get_text(strip=True), "ONCLICK:", a.get("onclick"), "HREF:", a.get("href"))
