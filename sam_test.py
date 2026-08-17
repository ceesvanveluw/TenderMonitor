import os
import requests

api_key = os.environ["SAM_API_KEY"]

url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 200,
    "postedFrom": "08/01/2026",
    "postedTo": "08/17/2026"
}

response = requests.get(url, params=params)
data = response.json()

positive = {
    "crane": 20,
    "lifting": 20,
    "hoist": 20,
    "winch": 20,
    "marine": 15,
    "vessel": 15,
    "ship": 15,
    "shipyard": 20,
    "offshore": 20,
    "port": 10,
    "harbor": 10,
    "harbour": 10,
    "dock": 10,
    "terminal": 5,
    "dredg": 20,
    "handling": 15,
}

negative = {
    "school": -30,
    "conference": -30,
    "training": -20,
    "hotel": -20,
    "septic": -50,
    "waste": -40,
    "vehicle": -20,
    "medical": -30,
    "hospital": -30
}

results = []

for opp in data["opportunitiesData"]:

    title = str(opp.get("title", ""))
    score = 0

    text = title.lower()

    for word, points in positive.items():
        if word in text:
            score += points

    for word, points in negative.items():
        if word in text:
            score += points

    if score > 0:
        results.append((score, title))

results.sort(reverse=True)

print()
print("TOP MATCHES")
print("===========")

for score, title in results[:25]:
    print(f"{score:3} | {title}")
