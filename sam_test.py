import os
import csv
import json
import time
import requests
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================

SAM_API_KEY = os.getenv("SAM_API_KEY", "").strip()
BASE_URL = "https://api.sam.gov/opportunities/v2/search"

DAYS_BACK = 7
PAGE_SIZE = 1000
TOP_PER_PAGE = PAGE_SIZE
FINAL_TOP_N = 150

RAW_OUTPUT_FILE = "sam_raw.jsonl"
PAGE_SHORTLIST_FILE = "sam_page_shortlist.csv"
FINAL_SHORTLIST_FILE = "sam_shortlist.csv"
FINAL_JSON_FILE = "sam_shortlist.json"

REQUEST_SLEEP_SECONDS = 0.5
MAX_RETRIES = 3

# Procurement types:
# p = presolicitation
# o = solicitation
# k = combined synopsis/solicitation
# r = sources sought
# s = special notice
# a = award notice
#
# For sales intelligence, award notices are excluded for daily chasing.
PTYPE = "p,o,k,r,s"


# =========================
# SCORING
# =========================

HIGH_VALUE_TERMS = {
    "crane": 40,
    "cranes": 40,
    "pedestal crane": 55,
    "offshore crane": 60,
    "ship crane": 45,
    "marine crane": 50,
    "knuckle boom": 55,
    "active heave": 70,
    "ahc": 60,

    "winch": 35,
    "winches": 35,
    "deck equipment": 45,
    "lifting equipment": 45,
    "handling equipment": 35,
    "material handling": 25,
    "hoist": 25,
    "davit": 25,
    "davits": 25,

    "offshore": 35,
    "vessel": 30,
    "ship": 20,
    "shipyard": 30,
    "dry dock": 25,
    "drydock": 25,
    "floating dock": 25,
    "marine": 20,

    "subsea": 45,
    "rov": 35,
    "plsv": 55,
    "rsv": 50,
    "ahts": 45,
    "psv": 35,
    "osv": 35,
    "drillship": 55,
    "semi-submersible": 55,
    "semisubmersible": 55,
    "rig": 35,
    "drilling rig": 50,
    "bop": 45,

    "fpso": 55,
    "fso": 35,
    "turret": 45,
    "mooring": 35,
    "topside": 35,
    "topsides": 35,

    "fabrication": 20,
    "structural steel": 20,
    "hydraulic": 25,
    "hydraulics": 25,
    "electrical drive": 25,
    "automation": 15,
    "control system": 20,
}

MEDIUM_VALUE_TERMS = {
    "maintenance": 12,
    "repair": 12,
    "overhaul": 18,
    "inspection": 8,
    "certification": 8,
    "load test": 25,
    "load testing": 25,
    "installation": 12,
    "commissioning": 20,
    "upgrade": 25,
    "modernization": 25,
    "modernisation": 25,
    "refurbishment": 22,
    "spare parts": 15,
    "spares": 12,
    "parts": 5,
}

BAD_TERMS = {
    "janitorial": -40,
    "cleaning": -35,
    "custodial": -35,
    "lawn": -35,
    "landscaping": -35,
    "catering": -35,
    "food": -25,
    "restaurant": -25,
    "security guard": -35,
    "guard service": -35,
    "it support": -25,
    "software license": -25,
    "software licence": -25,
    "office supplies": -30,
    "furniture": -25,
    "medical": -30,
    "pharmaceutical": -35,
    "training course": -20,
    "consulting services": -15,
    "architect engineer": -15,
    "ae services": -15,
    "road": -25,
    "highway": -25,
    "bridge": -20,
    "vehicle": -25,
    "vehicles": -25,
    "truck": -25,
    "trucks": -25,
    "camion": -25,
    "camionnette": -25,
    "vehicule": -25,
    "vehicule": -25,
}

AGENCY_BOOST_TERMS = {
    "navy": 20,
    "naval": 20,
    "military sealift": 25,
    "coast guard": 20,
    "maritime administration": 20,
    "army corps": 10,
    "noaa": 10,
    "bureau of ocean energy": 15,
    "boem": 15,
    "bureau of safety": 15,
    "bsee": 15,
}

CLASSIFICATION_BOOSTS = {
    "20": 10,  # Ship and marine equipment, if used
    "J": 8,    # Maintenance, repair, rebuilding
    "K": 10,   # Modification of equipment
    "V": 8,    # Transportation / marine can sit here sometimes
    "Z": 5,    # Maintenance of real property, noisy but sometimes yard related
}


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_search_blob(record):
    fields = [
        record.get("title"),
        record.get("solicitationNumber"),
        record.get("fullParentPathName"),
        record.get("organizationName"),
        record.get("organizationType"),
        record.get("type"),
        record.get("baseType"),
        record.get("naicsCode"),
        record.get("classificationCode"),
        record.get("archiveType"),
        record.get("setAside"),
        record.get("description"),
    ]

    office = record.get("officeAddress") or {}
    if isinstance(office, dict):
        fields.extend([
            office.get("city"),
            office.get("state"),
            office.get("zip"),
        ])

    pop = record.get("placeOfPerformance") or {}
    if isinstance(pop, dict):
        fields.append(safe_text(pop))

    return " | ".join(safe_text(x) for x in fields).lower()


def score_record(record):
    blob = build_search_blob(record)

    score = 0
    reasons = []

    for term, points in HIGH_VALUE_TERMS.items():
        if term in blob:
            score += points
            reasons.append(f"+{points} {term}")

    for term, points in MEDIUM_VALUE_TERMS.items():
        if term in blob:
            score += points
            reasons.append(f"+{points} {term}")

    for term, points in BAD_TERMS.items():
        if term in blob:
            score += points
            reasons.append(f"{points} {term}")

    for term, points in AGENCY_BOOST_TERMS.items():
        if term in blob:
            score += points
            reasons.append(f"+{points} agency:{term}")

    classification = safe_text(record.get("classificationCode")).upper().strip()
    for prefix, points in CLASSIFICATION_BOOSTS.items():
        if classification.startswith(prefix):
            score += points
            reasons.append(f"+{points} class:{prefix}")

    notice_type = safe_text(record.get("type")).lower()
    base_type = safe_text(record.get("baseType")).lower()
    type_blob = notice_type + " " + base_type

    if "solicitation" in type_blob:
        score += 15
        reasons.append("+15 solicitation")

    if "sources sought" in type_blob:
        score += 10
        reasons.append("+10 sources sought")

    if "presolicitation" in type_blob or "pre solicitation" in type_blob:
        score += 10
        reasons.append("+10 presolicitation")

    if "award" in type_blob:
        score -= 15
        reasons.append("-15 award notice")

    return score, reasons


# =========================
# SAM FETCHING
# =========================

def format_sam_date(dt):
    return dt.strftime("%m/%d/%Y")


def sam_get_page(posted_from, posted_to, offset):
    if not SAM_API_KEY:
        raise RuntimeError("SAM_API_KEY environment variable is missing.")

    params = {
        "api_key": SAM_API_KEY,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": PAGE_SIZE,
        "offset": offset,
        "ptype": PTYPE,
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(BASE_URL, params=params, timeout=60)

            if response.status_code == 429:
                sleep_for = 10 * attempt
                print(f"Rate limited. Sleeping {sleep_for} seconds.")
                time.sleep(sleep_for)
                continue

            response.raise_for_status()
            return response.json()

        except Exception as exc:
            last_error = exc
            sleep_for = 5 * attempt
            print(f"Error on offset {offset}, attempt {attempt}: {exc}")
            time.sleep(sleep_for)

    raise RuntimeError(f"Failed to fetch offset {offset}: {last_error}")


def extract_records(payload):
    if not isinstance(payload, dict):
        return []

    for key in ["opportunitiesData", "opportunityData", "data", "results"]:
        value = payload.get(key)
        if isinstance(value, list):
            return value

    return []


def get_total_records(payload):
    value = payload.get("totalRecords", 0)
    try:
        return int(value)
    except Exception:
        return 0


def normalise_sam_record(record, score, reasons):
    notice_id = safe_text(record.get("noticeId") or record.get("noticeID") or record.get("id"))
    solnum = safe_text(record.get("solicitationNumber"))
    title = safe_text(record.get("title"))

    org = (
        record.get("fullParentPathName")
        or record.get("organizationName")
        or record.get("department")
        or record.get("subtier")
        or ""
    )

    url = record.get("uiLink") or ""
    description_link = record.get("description") or ""

    if not url and notice_id:
        url = f"https://sam.gov/opp/{notice_id}/view"

    return {
        "source": "SAM",
        "source_id": notice_id or solnum or title,
        "title": title,
        "organisation": safe_text(org),
        "posted_date": safe_text(record.get("postedDate")),
        "closing_date": safe_text(record.get("responseDeadLine") or record.get("reponseDeadLine")),
        "notice_type": safe_text(record.get("type") or record.get("baseType")),
        "classification_code": safe_text(record.get("classificationCode")),
        "naics_code": safe_text(record.get("naicsCode")),
        "description": safe_text(description_link),
        "url": safe_text(url),
        "raw_score": score,
        "score_reasons": "; ".join(reasons[:25]),
        "raw_record": record,
    }


# =========================
# OUTPUT
# =========================

CSV_FIELDS = [
    "source",
    "source_id",
    "title",
    "organisation",
    "posted_date",
    "closing_date",
    "notice_type",
    "classification_code",
    "naics_code",
    "description",
    "url",
    "raw_score",
    "score_reasons",
]


def write_csv(path, records):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for rec in records:
            row = {field: rec.get(field, "") for field in CSV_FIELDS}
            writer.writerow(row)


def write_json(path, records):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def append_raw_jsonl(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def dedupe_records(records):
    seen = set()
    output = []

    for rec in records:
        key = (
            rec.get("source"),
            rec.get("source_id"),
            rec.get("title"),
            rec.get("organisation"),
        )

        if key in seen:
            continue

        seen.add(key)
        output.append(rec)

    return output


def print_top_150(final_shortlist):
    print("")
    print("=" * 120)
    print("TOP 150 SAM OPPORTUNITIES")
    print("=" * 120)

    for idx, rec in enumerate(final_shortlist[:150], start=1):
        title = safe_text(rec.get("title"))[:160].replace("\n", " ").replace("\r", " ")
        organisation = safe_text(rec.get("organisation"))[:120].replace("\n", " ").replace("\r", " ")
        closing = safe_text(rec.get("closing_date"))
        url = safe_text(rec.get("url"))
        reasons = safe_text(rec.get("score_reasons"))[:180].replace("\n", " ").replace("\r", " ")

        print(
            f"{idx:03d} | "
            f"Score={rec.get('raw_score', 0)} | "
            f"Close={closing} | "
            f"{title} | "
            f"{organisation} | "
            f"{url} | "
            f"Reasons={reasons}"
        )


# =========================
# MAIN
# =========================

def run_sam_monitor():
    today = datetime.utcnow().date()
    start = today - timedelta(days=DAYS_BACK)

    posted_from = format_sam_date(datetime.combine(start, datetime.min.time()))
    posted_to = format_sam_date(datetime.combine(today, datetime.min.time()))

    print(f"SAM pull window: {posted_from} to {posted_to}")
    print(f"Page size: {PAGE_SIZE}")
    print(f"Top per page: {TOP_PER_PAGE}")
    print(f"Final top N: {FINAL_TOP_N}")

    open(RAW_OUTPUT_FILE, "w", encoding="utf-8").close()

    all_scored_records = []

    first_payload = sam_get_page(posted_from, posted_to, offset=0)
    total_records = get_total_records(first_payload)
    first_records = extract_records(first_payload)

    total_pages = (total_records + PAGE_SIZE - 1) // PAGE_SIZE

    print(f"Total records reported by SAM: {total_records}")
    print(f"Total pages to fetch: {total_pages}")

    for offset in range(total_pages):
        if offset == 0:
            records = first_records
        else:
            payload = sam_get_page(posted_from, posted_to, offset=offset)
            records = extract_records(payload)

        print(f"Fetched page offset {offset}: {len(records)} records")

        scored_page = []

        for raw in records:
            append_raw_jsonl(RAW_OUTPUT_FILE, raw)

            score, reasons = score_record(raw)
            normalised = normalise_sam_record(raw, score, reasons)
            scored_page.append(normalised)

        scored_page.sort(key=lambda x: x.get("raw_score", 0), reverse=True)

        page_winners = scored_page[:TOP_PER_PAGE]
        all_scored_records.extend(page_winners)

        best_score = page_winners[0]["raw_score"] if page_winners else "n/a"
        print(f"Page {offset}: kept {len(page_winners)} candidates. Best score: {best_score}")

        time.sleep(REQUEST_SLEEP_SECONDS)

    all_scored_records = dedupe_records(all_scored_records)
    all_scored_records.sort(key=lambda x: x.get("raw_score", 0), reverse=True)

    final_shortlist = all_scored_records[:FINAL_TOP_N]

    write_csv(PAGE_SHORTLIST_FILE, all_scored_records)
    write_csv(FINAL_SHORTLIST_FILE, final_shortlist)
    write_json(FINAL_JSON_FILE, final_shortlist)

    print_top_150(final_shortlist)

    print("")
    print("=" * 120)
    print("FILES CREATED")
    print("=" * 120)
    print(f"Raw dump        : {RAW_OUTPUT_FILE}")
    print(f"Page shortlist  : {PAGE_SHORTLIST_FILE}")
    print(f"Final shortlist : {FINAL_SHORTLIST_FILE}")
    print(f"JSON shortlist  : {FINAL_JSON_FILE}")
    print(f"Final candidates: {len(final_shortlist)}")
    print("Done.")


if __name__ == "__main__":
    run_sam_monitor()
