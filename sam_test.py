import os
import requests
import json

api_key = os.environ["SAM_API_KEY"]

search_url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 1,
    "postedFrom": "08/01/2026",
    "postedTo": "08/17/2026"
}

response = requests.get(search_url, params=params)

print("SEARCH STATUS:", response.status_code)

data = response.json()

first = data["opportunitiesData"][0]

desc_url = first["description"]

print()
print("DESCRIPTION URL")
print(desc_url)

print()
print("FETCHING DESCRIPTION")
print()

desc_response = requests.get(desc_url)

print("DESCRIPTION STATUS:", desc_response.status_code)

print()
print("RAW RESPONSE:")
print(desc_response.text[:3000])
