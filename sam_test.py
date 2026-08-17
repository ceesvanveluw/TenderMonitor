import os
import requests
import json

api_key = os.environ["SAM_API_KEY"]

url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 1,
    "postedFrom": "08/01/2026",
    "postedTo": "08/17/2026"
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

data = response.json()

print()
print("FULL FIRST OPPORTUNITY")
print("======================")
print()

print(json.dumps(data["opportunitiesData"][0], indent=2))
