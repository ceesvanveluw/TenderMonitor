import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://canadabuys.canada.ca"
SEARCH_URL = "https://canadabuys.canada.ca/en/tender-opportunities"

MAX_OUTPUT = 25

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
    "Referer": "https://canadabuys.canada.ca/",
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

    # French / bilingual CanadaBuys terms
    "maritime",
    "navire",
    "bateau",
    "grue",
    "levage",
    "treuil",
    "hydraulique",
    "portuaire",
    "dragage",
    "cale sèche",
    "cale seche",
    "réparation navale",
    "reparation navale",
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

    # Broader marine words, deliberately lower score
    "marine": 15,
    "maritime": 15,
    "ship": 10,
    "vessel": 10,
    "navire": 10,
    "boat": 5,
    "bateau": 5,
    "tug": 10,
    "remorqueur": 10,
    "port": 5,
    "harbour": 5,
    "harbor": 5,
    "dock": 5,
    "portuaire": 5,
    "cale sèche": 35,
    "cale seche": 35,
    "réparation navale": 30,
    "reparation navale": 30
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

    # Vehicle penalties. Do not search these actively.
    "truck": -15,
    "pickup": -20,
    "camion": -15,
    "camionnette": -15,
    "vehicule": -10,
    "véhicule": -10,

    # Known false positives / weak hits
    "isle-aux-grues": -40,
    "l'isle-aux-grues": -40,
    "scénique": -25,
    "scenique": -25,
    "sonorisation": -25,
    "recyclables": -30,
    "matières recyclables": -30,

    # French noise
    "santé": -40,
    "école": -50,
    "enfants": -50,
    "famille": -50,
    "toiture": -50,
    "nettoyage": -40
}


def clean_text(value):
    if not value:
        return ""

    value = re.sub(r"\s+", " ", value)
    return value.strip()


def get_lines_from_soup(soup):
    text = soup.get_text("\n", strip=True)
    lines = []

    for line in text.split("\n"):
        line = clean_text(line)
        if line:
            lines.append(line)

    return lines


def get_value_after_label(lines, labels):
    labels_lower = [label.lower() for label in labels]

    for i, line in enumerate(lines):
        line_lower = line.lower()

        for label in labels_lower:
            if line_lower == label:
                if i + 1 < len(lines):
                    return lines[i + 1]

            if line_lower.startswith(label + ":"):
                return clean_text(line.split(":", 1)[1])

    return ""


def get_description_after_label(lines):
    description_labels = [
        "description",
        "tender description",
        "procurement description",
        "notice description",
        "description of work",
        "summary",
        "details"
    ]

    stop_labels = [
        "closing date",
        "closing date and time",
        "organization",
        "contracting organization",
        "contact information",
        "contact",
        "documents",
        "attachments",
        "notice type",
        "category",
        "region",
        "location",
        "publication date",
        "amendment date",
        "unspsc",
        "gsin"
    ]

    description_labels_lower = [x.lower() for x in description_labels]
    stop_labels_lower = [x.lower() for x in stop_labels]

    for i, line in enumerate(lines):
        line_lower = line.lower()

        if line_lower in description_labels_lower or any(line_lower.startswith(label + ":") for label in description_labels_lower):

            collected = []

            if ":" in line:
                after_colon = clean_text(line.split(":", 1)[1])
                if after_colon:
                    collected.append(after_colon)

            for next_line in lines[i + 1:i + 15]:
                next_lower = next_line.lower()

                if next_lower in stop_labels_lower:
                    break

                if any(next_lower.startswith(label + ":") for label in stop_labels_lower):
                    break

                collected.append(next_line)

            description = clean_text(" ".join(collected))

            if description:
                return description[:1200]

    return ""


def get_detail_fields(url):
    detail = {
        "organization": "",
        "closing_date": "",
        "description": ""
    }

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        if r.status_code != 200:
            detail["description"] = f"Could not load detail page. Status: {r.status_code}"
            return detail

        soup = BeautifulSoup(r.text, "html.parser")
        lines = get_lines_from_soup(soup)

        detail["organization"] = get_value_after_label(
            lines,
            [
                "Organization",
                "Organisation",
                "Contracting organization",
                "Contracting authority",
                "Buyer",
                "Procuring entity"
            ]
        )

        detail["closing_date"] = get_value_after_label(
            lines,
            [
                "Closing date",
                "Closing date and time",
                "Date de clôture",
                "Date de fermeture",
                "Closing"
            ]
        )

        detail["description"] = get_description_after_label(lines)

        if not detail["description"]:
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                detail["description"] = clean_text(meta.get("content"))[:1200]

        return detail

    except Exception as e:
        detail["description"] = f"Error loading detail page: {e}"
        return detail


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

    # Small bonus if the tender appeared in multiple keyword searches
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


for item in results[:MAX_OUTPUT]:

    detail = get_detail_fields(item["url"])

    print()
    print("SCORE:", item["score"])
    print("TITLE:", item["title"])
    print("ORGANIZATION:", detail["organization"])
    print("CLOSING DATE:", detail["closing_date"])
    print("MATCHED WORDS:", ", ".join(item["matched_words"]))
    print("URL:", item["url"])

    if detail["description"]:
        print("DESCRIPTION:", detail["description"])
    else:
        print("DESCRIPTION: Not found on detail page with current parser.")

    print("-" * 100)


if not results:
    print("No candidates found.")