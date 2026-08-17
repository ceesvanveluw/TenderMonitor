import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/BusquedaLicitacionesResultados"

r = requests.get(
    url,
    timeout=30,
    verify=False
)

print("Status:", r.status_code)

html = r.text

print("\nSearching for keywords...\n")

keywords = [
    "WORK BOAT",
    "LANCHA",
    "Licitación",
    "NumeroLicitacion",
    "RedirectLicitaciones",
    "Ver detalle"
]

for keyword in keywords:
    print(keyword, "=", html.count(keyword))