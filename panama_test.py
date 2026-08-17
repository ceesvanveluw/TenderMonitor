import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 50)
print("PANAMA TENDER SCRAPER")
print("=" * 50)

url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/BusquedaLicitacionesResultados"

r = requests.get(
    url,
    timeout=30,
    verify=False
)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

titles = soup.find_all("p", class_="title")
numbers = soup.find_all("p", class_="id")

print()
print("FOUND TENDERS")
print("-" * 50)

for number, title in zip(numbers, titles):
    print(
        f"{number.get_text(strip=True)} | "
        f"{title.get_text(strip=True)}"
    )

print("-" * 50)