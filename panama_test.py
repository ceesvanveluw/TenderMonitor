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

# Submit search
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

print("POST Status:", r2.status_code)

html = r2.text

soup = BeautifulSoup(html, "html.parser")

print("\nTENDERS FOUND")
print("=" * 80)

for link in soup.find_all("a"):

    href = str(link.get("href"))

    if "RedirectLicitaciones" in href:

        title = link.get_text(" ", strip=True)

        print(title)
        print(href)
        print("-" * 80)