import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()

# STEP 1
url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/Welcome"

r = session.get(
    url,
    verify=False,
    timeout=30
)

print("GET Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

token = soup.find(
    "input",
    {"name": "__RequestVerificationToken"}
)

if token:
    token = token.get("value")
else:
    token = ""

print("Token found:", bool(token))

# STEP 2
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

print("HTML Length:", len(html))
print("RedirectLicitaciones =", html.count("RedirectLicitaciones"))
print("Ver detalle =", html.count("Ver detalle"))
print("NumeroLicitacion =", html.count("NumeroLicitacion"))

print("\nFIRST 2000 CHARS\n")
print(html[:2000])