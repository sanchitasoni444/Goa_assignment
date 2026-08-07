import requests
from bs4 import BeautifulSoup

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Step 1: Set month=3 and year=2026
session.get("https://impds.nic.in/sale/stateUnautmated?month=3&year=2026", headers=headers)

# Step 2: Request districtByCountryAjax for North Goa (585)
resp_north = session.get("https://impds.nic.in/sale/districtByCountryAjax?stateCode=585", headers=headers)
print("districtByCountryAjax status:", resp_north.status_code)

soup_north = BeautifulSoup(resp_north.text, "html.parser")
with open("./north_goa_ajax.html", "w", encoding="utf-8") as f:
    f.write(soup_north.prettify())

print("\nAll links/buttons/onclicks in North Goa page:")
for tag in soup_north.find_all(True):
    if tag.get("onclick") or "fps" in tag.text.lower() or "fair price" in tag.text.lower():
        print(f"<{tag.name} id='{tag.get('id')}' class='{tag.get('class')}' onclick='{tag.get('onclick')}'>{tag.text.strip()[:100]}</{tag.name}>")
