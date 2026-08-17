import json
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://apps.pancanal.com"

CATEGORIES = [
    "Ship & Marine Equipment",
    "Materials Handling",
    "Hydraulic"
]

session = requests.Session()

# Get token once
r = session.get(
    f"{BASE_URL}/sli/LicitacionesBusqueda/Welcome",
    verify=False,
    timeout=30
)

soup = BeautifulSoup(r.text, "html.parser")

token = soup.find(
    "input",
    {"name": "__RequestVerificationToken"}
).get("value")

all_tenders = []

for category in CATEGORIES:

    payload = {
        "__RequestVerificationToken": token,
        "CategoriaSeleccionadaID": category,
        "EstatusSeleccionadoID": "TODOS"
    }

    r2 = session.post(
        f"{BASE_URL}/sli/LicitacionesBusqueda/LicitacionesBusquedaParametros",
        data=payload,
        verify=False,
        timeout=30
    )

    soup = BeautifulSoup(r2.text, "html.parser")

    print("\n")
    print("=" * 100)
    print(f"CATEGORY: {category}")
    print("=" * 100)

    for well in soup.find_all("div", class_="well"):

        number = ""
        title = ""
        closing_date = ""
        detail_url = ""

        link = well.find("a")

        if link:
            number = link.get_text(strip=True)

            href = link.get("href")

            if href:
                if href.startswith("/"):
                    detail_url = BASE_URL + href
                else:
                    detail_url = href

        title_tag = well.find("p", class_="title")

        if title_tag:
            title = title_tag.get_text(" ", strip=True)

        date_tag = well.find("p", class_="date")

  