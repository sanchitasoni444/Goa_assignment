from bs4 import BeautifulSoup

with open("./fps_158500200184_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for div in soup.find_all(class_="info"):
    print("INFO DIV:", div.parent.get_text(separator=' | ', strip=True))
