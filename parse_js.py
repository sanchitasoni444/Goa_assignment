from bs4 import BeautifulSoup

with open("./impds_edge.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

scripts = soup.find_all("script")
for i, s in enumerate(scripts):
    text = s.get_text()
    if "liveStatesdata" in text or "stateData" in text or "OnorcStateWisePage" in text or "myModal" in text:
        print(f"--- Script {i} ---")
        print(text[:2000])

print("\n--- ALL MODALS DETAILED ---")
for modal in soup.find_all(class_="modal"):
    print(f"Modal ID: {modal.get('id')}")
    print(modal.get_text(separator=' ', strip=True)[:300])
