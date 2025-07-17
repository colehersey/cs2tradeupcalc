import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

API_KEY = os.getenv('CSFLOAT_API_KEY')
BASE_URL = 'https://csfloat.com/api/v1/listings'
PAGE_SIZE = 50  # Max allowed by API

HEADERS = {
    'Authorization': API_KEY
}

def get_all_listings(max_pages: int = 100) -> List[Dict]:
    """
    Fetch all active listings from CSFloat API, paginated.
    Returns a list of listing dicts.
    """
    all_listings = []
    for page in range(max_pages):
        params = {
            'page': page,
            'limit': PAGE_SIZE
        }
        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print(f"Error fetching page {page}: {resp.status_code}")
            break
        listings = resp.json()
        if not listings:
            break  # No more data
        all_listings.extend(listings)
    return all_listings 