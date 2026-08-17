import requests
from bs4 import BeautifulSoup

URL = "https://canadabuys.canada.ca/en/tender-opportunities?status%5B0%5D=1920&status%5B1%5D=87"

print("=" * 60)
print("CANADABUYS TEST")
print("=" * 60)

r = requests.get(
    URL,
    timeout=30
)

print("Status:", r.status_code)
print("Length:", len(r.text))

soup = BeautifulSoup(r.text, "html.parser")

print()
print("Page title:")
print(soup.title.text if soup.title else "No title")
