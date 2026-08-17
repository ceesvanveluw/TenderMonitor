import os
import requests

api_key = os.environ["SAM_API_KEY"]

url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 10,
    "postedFrom": "08/01/2026",
    "postedTo": "08/17/2026",
    "q": "crane"
}

print(params)

response = requests.get(url, params=params)

print("ACTUAL URL:")
print(response.url)

print("Status:", response.status_code)

data = response.json()

print("Total records:", data["totalRecords"])
