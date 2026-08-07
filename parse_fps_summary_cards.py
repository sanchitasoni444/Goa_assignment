from bs4 import BeautifulSoup

with open("./fps_158500200184_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("--- ALL CARDS / BOXES ON FPS PAGE ---")
for card in soup.find_all(class_=["card", "info-box", "metro-nav-block", "custom-metro-nav-block", "dash-row1"]):
    print("CLASS:", card.get("class"), "TEXT:", card.get_text(separator=' | ', strip=True)[:150])

print("\n--- CARDS WITH NUMBERS / SUMMARY VALUES ---")
for box in soup.find_all(class_=["state_count", "itemTitle", "counter", "font-lato"]):
    print("PARENT CLASS:", box.parent.get("class"), "TEXT:", box.get_text(separator=' | ', strip=True))
