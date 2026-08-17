import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://apps.pancanal.com"

session = requests.Session()

# Get search page and token
url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/Welcome"

r = session.get(
    url,
    verify=False,
    timeout=30
)

soup = BeautifulSoup(r.text, "html.parser")

token = soup.find(
    "input",
    {"name": "__RequestVerificationToken"}
).get("value")

# Submit Ship & Marine Equipment search
payload = {
    "__RequestVerificationToken": token,
    "CategoriaSeleccionadaID": "Ship & Marine Equipment",
    "EstatusSeleccionadoID": "TODOS"
}

post_url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/LicitacionesBusquedaParametros"

r2 = session.post(
    post_url,
    data=payload,
    verify=False,
    timeout=30
)

soup = BeautifulSoup(r2.text, "html.parser")

print("\nPANAMA TENDERS\n")
print("=" * 120)

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

    dates = well.find_all("p", class_="date")

    if dates:
        closing_date = dates[0].get_text(" ", strip=True)

    if number:
        print(f"RFQ: {number}")
        print(f"TITLE: {title}")
        print(f"CLOSES: {closing_date}")
        print(f"URL: {detail_url}")
        print("-" * 120)