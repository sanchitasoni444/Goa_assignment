from bs4 import BeautifulSoup

with open("./north_goa_ajax.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("--- ALL LINKS AND BUTTONS IN NORTH GOA AJAX ---")
for tag in soup.find_all(['a', 'button', 'div', 'tr', 'td']):
    onclick = tag.get("onclick")
    href = tag.get("href")
    text = tag.text.strip()
    if onclick or "livefps" in str(onclick).lower() or "fps" in text.lower() or "fair price" in text.lower():
        print(f"<{tag.name} class='{tag.get('class')}' href='{href}' onclick='{onclick}'>{text[:80]}</{tag.name}>")
