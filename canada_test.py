import requests
from bs4 import BeautifulSoup

BASE_URL = "https://canadabuys.canada.ca/en/tender-opportunities"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}

params = {
    "status[0]": "1920",
    "status[1]": "87",
    "words": "marine"
}

r = requests.get(
    BASE_URL,
    params=params,
    headers=headers,
    timeout=30
)

print("Status:", r.status_code)
print()

html = r.text

print("marine count =", html.lower().count("marine"))
print("vessel count =", html.lower().count("vessel"))
print("ship count =", html.lower().count("ship"))
print()

soup = BeautifulSoup(html, "html.parser")

for link in soup.find_all("a"):

    href = str(link.get("href"))

    if "/en/tender-opportunities/tender-notice/" in href:

        title = link.get_text(" ", strip=True)

        if len(title) > 5:

            print(title)