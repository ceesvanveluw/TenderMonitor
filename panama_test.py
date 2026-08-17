import requests

print("PANAMA TEST START")

url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/BusquedaLicitacionesResultados"

r = requests.get(url, timeout=30)

print("Status:", r.status_code)
print("Length:", len(r.text))

print("PANAMA TEST END")
