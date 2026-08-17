import requests
from bs4 import BeautifulSoup

URL = "https://canadabuys.canada.ca/en/tender-opportunities?status%5B0%5D=1920&status%5B1%5D=87"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}

r = requests.get(
    URL,
    headers=headers,
    timeout=30
)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

print("\nFORMS")
print("=" * 100)

for form in soup.find_all("form"):

    print("ACTION:", form.get("action"))
    print()

    for inp in form.find_all(["input", "select"]):

        print(
            "NAME:",
            inp.get("name"),
            "| ID:",
            inp.get("id")
        )

    print("\n" + "=" * 100)