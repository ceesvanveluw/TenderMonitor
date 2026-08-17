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