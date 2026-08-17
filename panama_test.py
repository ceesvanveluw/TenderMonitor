import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 50)
print("PANAMA TEST START")
print("=" * 50)

url = "https://apps.pancanal.com/sli/LicitacionesBusqueda/BusquedaLicitacionesResultados"

try:
    r = requests.get(
        url,
        timeout=30,
        verify=False
    )

    print("Status:", r.status_code)
    print("Length:", len(r.text))

    print("First 500 characters:")
    print(r.text[:500])

except Exception as e:
    print("ERROR:", str(e))

print("=" * 50)
print("PANAMA TEST END")
print("=" * 50)