import os
import requests

api_key = os.environ["SAM_API_KEY"]

url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 1,
    "postedFrom": "08/01/2026",
    "postedTo": "08/17/2026"
}

response = requests.get(url, params=params)
data = response.json()

first = data["opportunitiesData"][0]

desc_url = first["description"]

print("DESCRIPTION URL")
print(desc_url)

print()
print("DOWNLOADING DESCRIPTION...")
print()

desc_response = requests.get(desc_url)

print("STATUS:", desc_response.status_code)

print()
print(desc_response.text[:5000])
