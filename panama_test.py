import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()

# Step 1 - get search page
url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/Welcome"

r = session.get(
    url,
    timeout=30,
    verify=False
)

print("GET Status:", r.status_code)

# Step 2 - simulate Ship & Marine Equipment search
search_url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/LicitacionesBusquedaParametros"

payload = {
    "CategoriaSeleccionadaID": "Ship & Marine Equipment",
    "EstatusSeleccionadoID": "TODOS"
}

r2 = session.post(
    search_url,
    data=payload,
    timeout=30,
    verify=False
)

print("POST Status:", r2.status_code)

html = r2.text

print("Length:", len(html))
print("RedirectLicitaciones =", html.count("RedirectLicitaciones"))
print("Ver detalle =", html.count("Ver detalle"))
print("NumeroLicitacion =", html.count("NumeroLicitacion"))

print("\nFIRST 3000 CHARACTERS\n")
print(html[:3000])