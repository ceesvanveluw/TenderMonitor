import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/Welcome"

r = requests.get(
    url,
    timeout=30,
    verify=False
)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

print("\nINPUT FIELDS")
print("=" * 80)

for inp in soup.find_all("input"):
    print(
        "name=", inp.get("name"),
        "| id=", inp.get("id"),
        "| value=", inp.get("value")
    )

print("\nSELECT FIELDS")
print("=" * 80)

for sel in soup.find_all("select"):
    print(
        "name=", sel.get("name"),
        "| id=", sel.get("id")
    )

print("\nFORMS")
print("=" * 80)

for form in soup.find_all("form"):
    print("ACTION =", form.get("action"))
