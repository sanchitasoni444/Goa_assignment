from bs4 import BeautifulSoup

with open("./goa_state_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("--- DISTRICT AREA / CARD HTML ---")
dist_area = soup.find(class_=["districtArea", "custom-metro-nav-block"])
if dist_area:
    print(dist_area.prettify()[:1000])

print("\n--- ALL ONCLICK FUNCTIONS IN GOA PAGE ---")
for el in soup.find_all(True):
    if el.get("onclick"):
        print(f"<{el.name} class='{el.get('class')}' onclick='{el.get('onclick')}'>{el.text.strip()[:60]}</{el.name}>")

print("\n--- SCRIPTS IN GOA PAGE ---")
for i, s in enumerate(soup.find_all("script")):
    text = s.get_text()
    if "district" in text.lower() or "livedistrict" in text.lower() or "fps" in text.lower():
        print(f"=== SCRIPT {i} ===")
        print(text[:1500])
