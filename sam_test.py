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

print("STATUS:", response.status_code)

print()
print("RAW RESPONSE")
print("============")
print(response.text[:5000])
