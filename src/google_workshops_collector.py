import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
from config import (
    LAT,
    LNG,
    SEARCH_RADIUS
)

# =========================
# LOAD ENVIRONMENT VARIABLES
# =========================
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

# =========================
# GOOGLE PLACES API URL
# =========================
URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# =========================
# SEARCH TYPES
# =========================
SEARCH_TYPES = [
    "car_repair"
]

# =========================
# STORE RESULTS
# =========================
all_results = []

# =========================
# LOOP THROUGH TYPES
# =========================
for search_type in SEARCH_TYPES:

    print(f"\nSearching for: {search_type}")

    params = {
        "location": f"{LAT},{LNG}",
        "radius": SEARCH_RADIUS,
        "type": search_type,
        "key": API_KEY
    }

    # =========================
    # FIRST PAGE
    # =========================
    response = requests.get(URL, params=params)

    data = response.json()

    page_number = 1

    while True:

        print(
            f"Found {len(data.get('results', []))} results "
            f"on page {page_number}"
        )

        # =========================
        # EXTRACT RESULTS
        # =========================
        for place in data.get("results", []):

            all_results.append({

                "business_type": search_type,

                "place_id": place.get("place_id"),

                "name": place.get("name"),

                "address": place.get("vicinity"),

                "rating": place.get("rating"),

                "user_ratings_total": place.get("user_ratings_total"),

                "business_status": place.get("business_status"),

                "latitude": place.get("geometry", {})
                                 .get("location", {})
                                 .get("lat"),

                "longitude": place.get("geometry", {})
                                  .get("location", {})
                                  .get("lng")
            })

        # =========================
        # CHECK NEXT PAGE
        # =========================
        next_page_token = data.get("next_page_token")
        print(f"Next page token exists? {next_page_token is not None}")

        if not next_page_token:
            break

        print(f"Next page found. Loading page {page_number + 1}...")

        # Google requires a short delay
        time.sleep(3)

        response = requests.get(
            URL,
            params={
                "pagetoken": next_page_token,
                "key": API_KEY
            }
        )

        data = response.json()

        page_number += 1

# =========================
# CREATE DATAFRAME
# =========================
df = pd.DataFrame(all_results)

# =========================
# REMOVE DUPLICATES
# =========================
df = df.drop_duplicates(subset="place_id")

# =========================
# CREATE OUTPUT DIRECTORY
# =========================
os.makedirs("data/raw", exist_ok=True)

# =========================
# SAVE CSV
# =========================
df.to_csv(
    "data/raw/workshops_capao_redondo.csv",
    index=False
)

# =========================
# PREVIEW RESULTS
# =========================
print("\nCollection completed.")

print(f"\nTotal workshops found: {len(df)}")

print("\nSample data:")
print(df.head())