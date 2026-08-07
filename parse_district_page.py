from bs4 import BeautifulSoup

with open("./north_goa_district_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

print("--- ALL LINKS AND BUTTONS ON NORTH GOA DISTRICT PAGE ---")
for tag in soup.find_all(['a', 'button', 'div']):
    text = tag.text.strip()
    onclick = tag.get("onclick")
    href = tag.get("href")
    if onclick or href or "fps" in text.lower() or "fair" in text.lower() or "240" in text:
        print(f"<{tag.name} class='{tag.get('class')}' href='{href}' onclick='{onclick}'>{text[:100]}</{tag.name}>")
