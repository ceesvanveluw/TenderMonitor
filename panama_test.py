import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
print("=" * 100)

for well in soup.find_all("div", class_="well"):

    number = ""

    link = well.find("a")

    if link:
        number = link.get_text(strip=True)

    title_tag = well.find("p", class_="title")

    title = ""

    if title_tag:
        title = title_tag.get_text(" ", strip=True)

    dates = well.find_all("p", class_="date")

    closing_date = ""

    if dates:
        closing_date = dates[0].get_text(" ", strip=True)

    if number:
        print(f"RFQ: {number}")
        print(f"TITLE: {title}")
        print(f"CLOSES: {closing_date}")
        print("-" * 100)