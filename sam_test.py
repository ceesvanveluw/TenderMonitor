# NEXT STEPS
#
# 1. Verify limit=1000 works
# 2. Verify date filtering works
# 3. Verify top 20 quality
# 4. Add description retrieval for top 20
# 5. Add Power Automate POST
# 6. Send Outlook digest

import os
import requests
from datetime import datetime, timedelta

api_key = os.environ["SAM_API_KEY"]

# Last 7 days
today = datetime.utcnow()
week_ago = today - timedelta(days=7)

posted_from = week_ago.strftime("%m/%d/%Y")
posted_to = today.strftime("%m/%d/%Y")

url = "https://api.sam.gov/opportunities/v2/search"

params = {
    "api_key": api_key,
    "limit": 1000,
    "offset": 0,
    "postedFrom": posted_from,
    "postedTo": posted_to
}

print("========================================================")
print("SAM TENDER DIGEST")
print("========================================================")
print(f"Period: {posted_from} - {posted_to}")
print()

response = requests.get(url, params=params)

# Quota handling
if response.status_code == 429:
    print("SAM API QUOTA EXCEEDED")
    print("------------------------------------")
    print(response.text)
    exit(0)

# Generic API error
if response.status_code != 200:
    print(f"API ERROR: {response.status_code}")
    print(response.text)
    exit(0)

data = response.json()

if "opportunitiesData" not in data:
    print("No opportunitiesData returned.")
    print(data)
    exit(0)

print(f"Total records found : {data.get('totalRecords', '?')}")
print(f"Records retrieved   : {len(data['opportunitiesData'])}")
print(f"Limit returned      : {data.get('limit', '?')}")
print(f"Offset returned     : {data.get('offset', '?')}")
print()

# Reject obvious rubbish sectors
excluded_prefixes = [
    "11",   # Agriculture
    "21",   # Mining
    "22",   # Utilities
    "44", "45",
    "51",
    "52",
    "53",
    "61",
    "62",
    "71",
    "72",
    "81",
    "92"
]

positive = {
    "crane": 60,
    "lifting": 50,
    "lift": 30,
    "hoist": 50,
    "winch": 60,
    "offshore": 70,
    "dredg": 80,
    "marine construction": 80,
    "ship": 20,
    "vessel": 30,
    "shipyard": 10,
    "marine": 10,
    "naval": 10,
    "port": 25,
    "harbor": 25,
    "harbour": 25,
    "terminal": 20,
    "dock": 20,
    "quay": 30,
    "cargo": 25,
    "handling": 30,
    "jackup": 80,
    "heavy lift": 80,
    "pipeline": 40,
    "barge": 40,
    "mooring": 40,
    "anchor": 40
}

negative = {
    "conference": -100,
    "training": -50,
    "septic": -150,
    "toilet": -150,
    "waste": -100,
    "medical": -100,
    "hospital": -100,
    "school": -100,
    "vehicle": -40,
    "fabric": -120,
    "cloth": -120,
    "uniform": -120,
    "apparel": -120,
    "hose": -80,
    "gasket": -80,
    "seal": -80,
    "bearing": -60,
    "filter": -80,
    "audio": -150,
    "video": -150,
    "camera": -100,
    "software": -100,
    "license": -100,
    "food": -150,
    "catering": -150,
    "water cooler": -150,
    "bottled water": -150,
    "chemical": -100,
    "cyanide": -150,
    "furniture": -150,
    "chair": -150,
    "desk": -150,
    "cleaning": -150,
    "janitorial": -150,
    "housekeeping": -150
}

results = []

for opp in data["opportunitiesData"]:

    title = str(opp.get("title", ""))
    agency = str(opp.get("fullParentPathName", ""))
    naics = str(opp.get("naicsCode", ""))
    classification = str(opp.get("classificationCode", ""))
    notice_id = str(opp.get("noticeId", ""))

    reject = False

    for prefix in excluded_prefixes:
        if naics.startswith(prefix):
            reject = True
            break

    if reject:
        continue

    text = (title + " " + agency).lower()
    title_text = title.lower()

    score = 0

    # Title matches count double
    for word, points in positive.items():
        if word in title_text:
            score += points * 2

    # General matches
    for word, points in positive.items():
        if word in text:
            score += points

    # Negative matches
    for word, points in negative.items():
        if word in text:
            score += points

    agency_lower = agency.lower()

    if "army corps of engineers" in agency_lower:
        score += 50

    if "coast guard" in agency_lower:
        score += 30

    if "maritime administration" in agency_lower:
        score += 50

    if "port authority" in agency_lower:
        score += 40

    if "navsea" in agency_lower:
        score += 20

    if score > 0:
        results.append({
            "score": score,
            "title": title,
            "agency": agency,
            "naics": naics,
            "classification": classification,
            "notice_id": notice_id
        })

results = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

print()
print("========================================================")
print("TOP 20 CANDIDATES")
print("========================================================")
print()

for item in results[:20]:

    print("--------------------------------------------------------")
    print(f"SCORE : {item['score']}")
    print()
    print("TITLE")
    print(item['title'])
    print()
    print("AGENCY")
    print(item['agency'])
    print()
    print(f"NAICS          : {item['naics']}")
    print(f"CLASSIFICATION : {item['classification']}")
    print(f"NOTICE ID      : {item['notice_id']}")
    print("--------------------------------------------------------")
    print()

print(f"Candidates returned: {len(results)}")
