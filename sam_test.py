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
    "44", "45",  # Retail
    "51",   # Media
    "52",   # Finance
    "53",   # Real Estate
    "61",   # Education
    "62",   # Healthcare
    "71",   # Recreation
    "72",   # Hotels/Food
    "81",   # Personal Services
    "92"    # Public Administration
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
