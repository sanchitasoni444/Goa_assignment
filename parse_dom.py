from bs4 import BeautifulSoup

with open("./impds_edge.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("--- MODALS ---")
for modal in soup.find_all(class_="modal"):
    print("Modal ID:", modal.get("id"), "Class:", modal.get("class"))

print("\n--- NAV BAR ITEMS / MONTH YEAR ---")
for item in soup.find_all(class_=["nav", "navbar", "dropdown", "month"]):
    print(item.text.strip()[:100])

print("\n--- SUMMARY CARDS ---")
for card in soup.find_all(class_=["card", "box", "summary", "info-box", "counter"]):
    print(card.get_text(strip=True)[:100])

print("\n--- ALL BUTTONS / LINKS WITH onclick OR data-toggle ---")
for el in soup.find_all(['a', 'button', 'div']):
    if el.get('onclick') or el.get('data-toggle') or el.get('data-target') or 'month' in str(el.get('id', '')).lower() or 'state' in str(el.get('id', '')).lower():
        print(f"<{el.name} id='{el.get('id')}' class='{el.get('class')}' onclick='{el.get('onclick')}' data-toggle='{el.get('data-toggle')}' data-target='{el.get('data-target')}'>{el.text.strip()[:60]}</{el.name}>")
