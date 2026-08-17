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

print("Total records:", data["totalRecords"])
print()

for opp in data["opportunitiesData"][:10]:
    print("------------------------------------")
    
    title = opp.get("title", "No title")
    notice = opp.get("noticeId", "")
    
    print("Title:", title)
    print("Notice:", notice)
