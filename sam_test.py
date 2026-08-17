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

excluded_prefixes = [
    "11", "21", "22",
    "44", "45",
    "51", "52", "53",
    "61", "62",
    "71", "72",
    "81", "92"
]

positive = {
    "crane": 30,
    "lifting": 25,
    "lift": 20,
    "hoist": 25,
    "winch": 30,
    "marine": 20,
    "vessel": 20,
    "ship": 20,
    "shipyard": 30,
    "offshore": 30,
    "port": 15,
    "harbor": 15,
    "harbour": 15,
    "dock": 15,
    "terminal": 10,
    "dredg": 30,
    "handling": 20,
    "cargo": 15,
    "naval": 15
}

negative = {
    "conference": -50,
    "training": -30,
    "septic": -100,
    "toilet": -100,
    "waste": -100,
    "medical": -50,
    "hospital": -50,
    "school": -50,
    "vehicle": -40
}

results = []

for opp in data["opportunitiesData"]:

    title = str(opp.get("title", ""))
    parent = str(opp.get("fullParentPathName", ""))
    naics = str(opp.get("naicsCode", ""))
    classification = str(opp.get("classificationCode", ""))

    # NAICS reject filter
    reject = False

    for prefix in excluded_prefixes:
        if naics.startswith(prefix):
            reject = True
            break

    if reject:
        continue

    text = (title + " " + parent).lower()

    score = 0

    for word, points in positive.items():
        if word in text:
            score += points

    for word, points in negative.items():
        if word in text:
            score += points

    if score > 0:
        results.append({
            "score": score,
            "title": title,
            "parent": parent,
            "naics": naics,
            "classification": classification
        })

results = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

print("")
print("========================================================")
print("SAM TENDER DIGEST")
print("========================================================")
print("")

if len(results) == 0:
    print("No matches found.")
else:

    for item in results[:10]:

        print("--------------------------------------------------------")
        print(f"SCORE : {item['score']}")
        print("")
        print("TITLE:")
        print(item["title"])
        print("")
        print("AGENCY:")
        print(item["parent"])
        print("")
        print(f"NAICS          : {item['naics']}")
        print(f"CLASSIFICATION : {item['classification']}")
        print("--------------------------------------------------------")
        print("")
