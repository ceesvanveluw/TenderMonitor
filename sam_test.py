import os
import requests

api_key = os.environ["SAM_API_KEY"]

url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 10,
    "postedFrom": "08/01/2026",
    "postedTo": "08/17/2026"
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

data = response.json()

print()
print("TOP LEVEL FIELDS")
print("================")

for key in data.keys():
    print(key)

print()
print("FIRST OPPORTUNITY FIELDS")
print("========================")

first = data["opportunitiesData"][0]

for key in first.keys():
    print(key)
