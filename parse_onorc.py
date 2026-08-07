from bs4 import BeautifulSoup

with open("./impds_edge.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for i, s in enumerate(soup.find_all("script")):
    text = s.get_text()
    if "OnorcStateWisePage" in text or "myModal10" in text or "liveStatesdata" in text:
        print(f"=== SCRIPT {i} ===")
        print(text)
