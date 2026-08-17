import requests
from bs4 import BeautifulSoup

BASE_URL = "https://canadabuys.canada.ca"
SEARCH_URL = "https://canadabuys.canada.ca/en/tender-opportunities"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}

SEARCH_WORDS = [
    "marine",
    "vessel",
    "ship",
    "crane",
    "hoist",
    "winch",
    "hydraulic",
    "port",
    "harbour",
    "harbor",
    "dock",
    "dredging",
    "dredge",
    "offshore",
    "cargo",
    "lifting",
    "boat",
    "tug",
    "drydock",
    "refit",
    "maritime",
    "navire",
    "grue",
    "levage",
    "treuil",
    "hydraulique",
    "dragage",
    "cale sèche",
    "réparation navale",
    "remorqueur"
]

positive = {
    # Strong Huisman indicators
    "crane": 35,
    "grue": 35,
    "hoist": 30,
    "winch": 30,
    "treuil": 30,
    "hydraulic": 25,
    "hydraulique": 25,
    "drydock": 35,
    "drydocking": 35,
    "refit": 25,
    "dredg": 35,
    "dragage": 35,
    "offshore": 35,
    "lifting": 25,
    "levage": 25,
    "cargo": 20,

    # Weakened broad marine words
    "marine": 15,
    "maritime": 15,
    "ship": 10,
    "vessel": 10,
    "navire": 10,
    "boat": 5,
    "tug": 10,
    "port": 5,
    "harbour": 5,
    "harbor": 5,
    "dock": 5,
    "portuaire": 5,
    "remorqueur": 10
}

negative = {
    "medical": -50,
    "hospital": -50,
    "health": -40,
    "school": -50,
    "children": -50,
    "family": -50,
    "laboratory": -40,
    "pool": -40,
    "roof": -50,
    "sewage": -80,
    "sanitary": -80,
    "snow removal": -60,
    "cleaning": -40,
    "food": -40,
    "office": -30,

    # Vehicle penalties
    "truck": -15,
    "pickup": -20,
    "camion": -15,
    "camionnette": -15,
    "vehicule": -10,
    "véhicule": -10,

    # French noise
    "santé": -40,
    "école": -50,
    "enfants": -50,
    "famille": -50,
    "toiture": -50,
    "nettoyage": -40
}

seen = {}
total_links_seen = 0

for word in SEARCH_WORDS:

    params = {
        "status[0]": "1920",
        "status[1]": "87",
        "words": word
    }

    r = requests.get(
        SEARCH_URL,
        params=params,
        headers=headers,
        timeout=30
    )

    print(f"Search word: {word} | Status: {r.status_code}")

    if r.status_code != 200:
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.find_all("a"):

        href = str(link.get("href"))

        if "/en/tender-opportunities/tender-notice/" not in href:
            continue

        title = link.get_text(" ", strip=True)

        if len(title) < 8:
            continue

        if href.startswith("/"):
            url = BASE_URL + href
        else:
            url = href

        total_links_seen += 1

        if url not in seen:
            seen[url] = {
                "title": title,
                "url": url,
                "matched_words": set()
            }

        seen[url]["matched_words"].add(word)

results = []

for url, item in seen.items():

    title = item["title"]
    text = title.lower()

    score = 0

    for word, points in positive.items():
        if word in text:
            score += points

    for word, points in negative.items():
        if word in text:
            score += points

    score += len(item["matched_words"]) * 5

    if score >= 40:

        results.append({
            "score": score,
            "title": title,
            "url": url,
            "matched_words": sorted(item["matched_words"])
        })

results = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

print()
print("=" * 100)
print("CANADABUYS KEYWORD SEARCH SUMMARY")
print("=" * 100)
print(f"Search words used       : {len(SEARCH_WORDS)}")
print(f"Raw tender links seen   : {total_links_seen}")
print(f"Unique tenders found    : {len(seen)}")
print(f"Candidates >= 40 score  : {len(results)}")

print()
print("=" * 100)
print("TOP CANADABUYS CANDIDATES")
print("=" * 100)

for item in results[:30]:

    print()
    print("SCORE:", item["score"])
    print("TITLE:", item["title"])
    print("MATCHED WORDS:", ", ".join(item["matched_words"]))
    print("URL:", item["url"])
    print("-" * 100)

if not results:
    print("No candidates found.")