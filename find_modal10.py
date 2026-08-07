from bs4 import BeautifulSoup

with open("./impds_edge.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for tag in soup.find_all(True):
    if tag.get("data-target") == "#myModal10" or "myModal10" in str(tag.get("onclick")) or "July-2026" in tag.text or "July" in tag.text:
        print("TAG:", tag.name, "ATTRS:", tag.attrs, "TEXT:", tag.text.strip()[:100])
