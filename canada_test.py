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

html = r.text

keywords = [
    "Closing date",
    "Organization",
    "/en/tender-opportunities/tender-notice",
    "Tender notices",
    "Results per page",
    "Showing"
]

for keyword in keywords:
    print(keyword, "=", html.count(keyword))