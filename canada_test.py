import requests
from bs4 import BeautifulSoup

URL = "https://canadabuys.canada.ca/en/tender-opportunities?status%5B0%5D=1920&status%5B1%5D=87"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}

positive = {
    "crane": 30,
    "lifting": 25,
    "lift": 20,
    "hoist": 25,
    "winch": 30,
    "marine": 20,
    "vessel": 20,
    "ship": 20,
    "shipyard": 30,
    "offshore": 30,
    "port": 15,
    "harbor": 15,
    "harbour": 15,
    "dock": 15,
    "terminal": 10,
    "dredg": 30,
    "handling": 20,
    "cargo": 15,
    "naval": 15
}

negative = {
    "medical": -50,
    "hospital": -50,
    "roof": -50,
    "family": -50,
    "children": -50,
    "laboratory": -50,
    "pool": -50,
    "sewage": -100,
    "sanitary": -100
}

r = requests.get(
    URL,
    headers=headers,
    timeout=30
)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

results = []

for link in soup.find_all("a"):

    href = str(link.get("href"))

    if "/en/tender-opportunities/tender-notice/" not in href:
        continue

    title = link.get_text(" ", strip=True)

    if len(title) < 10:
        continue

    text = title.lower()

    score = 0

    for word, points in positive.items():
        if word in text:
            score += points

    for word, points in negative.items():
        if word in text:
            score += points

    if score > 0:

        results.append({
            "score": score,
            "title": title,
            "url": "https://canadabuys.canada.ca" + href
        })

results = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

print()
print("=" * 100)
print("TOP CANADABUYS CANDIDATES")
print("=" * 100)

for item in results[:20]:

    print()
    print("SCORE:", item["score"])
    print("TITLE:", item["title"])
    print("URL:", item["url"])
    print("-" * 100)

print()
print("Candidates returned:", len(results))