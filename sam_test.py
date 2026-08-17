import os
import requests
import json

api_key = os.environ["SAM_API_KEY"]

url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 20,
    "postedFrom": "08/01/2026",
    "postedTo": "08/17/2026"
}

response = requests.get(url, params=params)

data = response.json()

for opp in data["opportunitiesData"][:20]:

    print("------------------------------------")
    print("TITLE:", opp.get("title"))
    print("CLASSIFICATION:", opp.get("classificationCode"))
    print("NAICS:", opp.get("naicsCode"))
    print("PATH:", opp.get("fullParentPathName"))
