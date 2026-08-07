import requests
from bs4 import BeautifulSoup

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. Set Month=3 Year=2026
session.get("https://impds.nic.in/sale/stateUnautmated?month=3&year=2026", headers=headers)

# 2. Test liveFpsAjax or fpsByDistrictAjax or similar endpoint for stateCode=30, distCode=585
print("--- Requesting liveFpsAjax?stateCode=30&districtCode=585 ---")
resp_live = session.get("https://impds.nic.in/sale/liveFpsAjax?stateCode=30&districtCode=585", headers=headers)
print("liveFpsAjax status:", resp_live.status_code)
print("liveFpsAjax text snippet:", resp_live.text[:500])

print("\n--- Requesting fpsByDistrictAjax?stateCode=30&districtCode=585 ---")
resp_fps = session.get("https://impds.nic.in/sale/fpsByDistrictAjax?stateCode=30&districtCode=585", headers=headers)
print("fpsByDistrictAjax status:", resp_fps.status_code)
print("fpsByDistrictAjax text snippet:", resp_fps.text[:500])

# Let's also check stateUnautmated?month=3&year=2026&stateCode=30&districtCode=585
print("\n--- Requesting district fps page ---")
resp_dist_page = session.get("https://impds.nic.in/sale/districtUnautmated?month=3&year=2026&stateCode=30&districtCode=585", headers=headers)
print("districtUnautmated status:", resp_dist_page.status_code)
print("districtUnautmated text snippet:", resp_dist_page.text[:500])
