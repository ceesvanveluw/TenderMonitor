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

print("\nHTML LENGTH:", len(html))
print("\nNumeroLicitacion count:", html.count("NumeroLicitacion"))
print("RedirectLicitaciones count:", html.count("RedirectLicitaciones"))

idx = html.find("NumeroLicitacion")

print("\nFIRST OCCURRENCE POSITION:", idx)

if idx >= 0:
    print("\n================ CONTEXT ================\n")
    start = max(0, idx - 1000)
    end = min(len(html), idx + 3000)
    print(html[start:end])
    print("\n============= END CONTEXT =============\n")