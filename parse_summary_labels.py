from bs4 import BeautifulSoup

with open("./fps_158500200184_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for box in soup.find_all(class_=["custom-metro-nav-block", "metro-nav-block", "info-box"]):
    text = box.get_text(separator=' ', strip=True)
    if "Transaction" in text or "Authenticated" in text:
        print("BOX:", text)
