import os
import requests
import time
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import sys
import json

# Add calculator to path for SkinData import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from calculator.tradeup_engine import SkinData

load_dotenv()

@dataclass
class CSFloatConfig:
    """Configuration for CSFloat API"""
    api_key: str
    base_url: str = "https://csfloat.com/api/v1"
    max_requests_per_minute: int = 60

    def __post_init__(self):
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError("CSFloat API key not configured. Please set CSFLOAT_API_KEY in .env file")


class CSFloatAPI:
    """CSFloat API client for fetching CS2 skin market data"""

    def __init__(self):
        self.config = CSFloatConfig(
            api_key=os.getenv('CSFLOAT_API_KEY', ''),
            base_url=os.getenv('CSFLOAT_BASE_URL', 'https://csfloat.com/api/v1'),
            max_requests_per_minute=int(os.getenv('CSFLOAT_MAX_REQUESTS_PER_MINUTE', '60'))
        )

        # Create a session for connection reuse and better bot detection avoidance
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': self.config.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive'
        })

        self.last_request_time = 0
        self.request_count = 0
        self.minute_start_time = time.time()

    def _rate_limit(self):
        """Implement rate limiting to respect API limits"""
        current_time = time.time()

        # Reset counter if minute has passed
        if current_time - self.minute_start_time >= 60:
            self.request_count = 0
            self.minute_start_time = current_time

        # Check if we're hitting rate limit
        if self.request_count >= self.config.max_requests_per_minute:
            sleep_time = 60 - (current_time - self.minute_start_time) + 1
            print(f"Rate limit reached. Sleeping for {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
            self.request_count = 0
            self.minute_start_time = time.time()

        self.request_count += 1

    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection and authentication"""
        try:
            self._rate_limit()
            url = f"{self.config.base_url}/listings"
            params = {'limit': 1}

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return True, "API connection successful"
            elif response.status_code == 401:
                return False, "Authentication failed - check API key"
            elif response.status_code == 429:
                return False, "Rate limit exceeded"
            else:
                # Handle encoding issues with response text
                try:
                    error_text = response.text[:100] + "..." if len(response.text) > 100 else response.text
                except UnicodeDecodeError:
                    error_text = "Unable to decode error response"
                return False, f"API error: {response.status_code} - {error_text}"

        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def get_skin_listings(self, market_hash_name: str, limit: int = 10,
                         min_float: Optional[float] = None,
                         max_float: Optional[float] = None,
                         sort_by: str = "lowest_price") -> List[Dict]:
        """
        Get listings for a specific skin

        Args:
            market_hash_name: Full skin name (e.g., "AK-47 | Redline (Field-Tested)")
            limit: Number of listings to return
            min_float: Minimum float value filter
            max_float: Maximum float value filter
            sort_by: Sort method (lowest_price, highest_price, lowest_float, etc.)
        """
        try:
            self._rate_limit()
            url = f"{self.config.base_url}/listings"

            params = {
                'limit': min(limit, 50),  # API max is 50
                'sort_by': sort_by
            }

            # Only add market_hash_name if it's not empty
            if market_hash_name.strip():
                params['market_hash_name'] = market_hash_name

            if min_float is not None:
                params['min_float'] = min_float
            if max_float is not None:
                params['max_float'] = max_float

            response = self.session.get(url, params=params, timeout=15)

            if response.status_code == 200:
                if response.text.strip():
                    data = response.json()
                    # CSFloat API wraps listings in a 'data' field
                    if isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, list):
                        return data
                    else:
                        print(f"Unexpected response format for {market_hash_name}: {type(data)}")
                        return []
                else:
                    print(f"Empty response for {market_hash_name}")
                    return []
            else:
                print(f"Error fetching {market_hash_name}: {response.status_code} - {response.text[:200]}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Request error for {market_hash_name}: {str(e)}")
            return []

    def get_collection_skins(self, collection: str, rarity: str = None,
                           limit: int = 100) -> List[Dict]:
        """
        Get all skins from a specific collection

        Args:
            collection: Collection name (e.g., "Dust 2 Collection")
            rarity: Optional rarity filter
            limit: Maximum number of results
        """
        try:
            self._rate_limit()
            url = f"{self.config.base_url}/listings"

            params = {
                'collection': collection,
                'limit': min(limit, 50)
            }

            if rarity:
                params['rarity'] = rarity

            response = self.session.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                # CSFloat API wraps listings in a 'data' field
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    print(f"Unexpected response format for collection {collection}: {type(data)}")
                    return []
            else:
                print(f"Error fetching collection {collection}: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Request error for collection {collection}: {str(e)}")
            return []

    def convert_to_skin_data(self, csfloat_listing: Dict) -> SkinData:
        """
        Convert CSFloat listing format to our SkinData format

        CSFloat API structure:
        {
            "id": "...",
            "price": 260000,  # Price in cents
            "item": {
                "market_hash_name": "M4A4 | Poseidon (Factory New)",
                "collection": "The Gods and Monsters Collection",
                "rarity": 5,
                "float_value": 0.02796577662229538,
                "wear_name": "Factory New",
                "is_stattrak": false,
                "is_souvenir": false,
                ...
            }
        }
        """
        # Extract item data from the listing
        item_data = csfloat_listing.get('item', {})

        return SkinData(
            market_hash_name=item_data.get('market_hash_name', ''),
            collection=item_data.get('collection', ''),
            rarity=item_data.get('rarity', ''),
            float_value=float(item_data.get('float_value', 0.0)),
            price_cents=int(csfloat_listing.get('price', 0)),  # Price is at listing level
            wear_name=item_data.get('wear_name', ''),
            is_stattrak=item_data.get('is_stattrak', False),
            is_souvenir=item_data.get('is_souvenir', False)
        )

    def get_tradeup_input_suggestions(self, target_collection: str,
                                    input_rarity: str,
                                    max_budget_cents: int = 10000) -> List[SkinData]:
        """
        Get suggestions for input skins for a tradeup to target collection

        Args:
            target_collection: Collection you want to trade up to
            input_rarity: Rarity of input skins needed
            max_budget_cents: Maximum budget for all 10 input skins
        """
        # Get listings for input rarity skins that can trade up to target collection
        # This would require collection relationship mapping - simplified for now

        try:
            listings = self.get_collection_skins(target_collection, input_rarity, 50)

            suitable_skins = []
            budget_per_skin = max_budget_cents // 10

            for listing in listings:
                if listing.get('price', float('inf')) <= budget_per_skin:
                    skin_data = self.convert_to_skin_data(listing)
                    suitable_skins.append(skin_data)

            return suitable_skins[:20]  # Return top 20 options

        except Exception as e:
            print(f"Error getting tradeup suggestions: {str(e)}")
            return []

    def get_outcome_skins(self, target_collection: str, target_rarity: str) -> List[SkinData]:
        """
        Get all possible outcome skins for a tradeup

        Args:
            target_collection: Collection of outcome skins
            target_rarity: Rarity of outcome skins (one tier up from inputs)
        """
        try:
            listings = self.get_collection_skins(target_collection, target_rarity, 100)

            outcome_skins = []
            seen_skins = set()

            for listing in listings:
                skin_name = listing.get('market_hash_name', '')
                if skin_name not in seen_skins:
                    skin_data = self.convert_to_skin_data(listing)
                    outcome_skins.append(skin_data)
                    seen_skins.add(skin_name)

            return outcome_skins

        except Exception as e:
            print(f"Error getting outcome skins: {str(e)}")
            return []


# Legacy function for backward compatibility
def get_all_listings(max_pages: int = 100) -> List[Dict]:
    """
    Fetch all active listings from CSFloat API, paginated.
    Returns a list of listing dicts.
    """
    api = CSFloatAPI()
    all_listings = []
    page_size = 50

    for page in range(max_pages):
        try:
            api._rate_limit()
            url = f"{api.config.base_url}/listings"
            params = {
                'page': page,
                'limit': page_size
            }
            resp = api.session.get(url, params=params)
            if resp.status_code != 200:
                print(f"Error fetching page {page}: {resp.status_code}")
                break
            data = resp.json()
            # Handle CSFloat API response format
            if isinstance(data, dict) and 'data' in data:
                listings = data['data']
            else:
                listings = data

            if not listings:
                break  # No more data
            all_listings.extend(listings)
        except Exception as e:
            print(f"Error on page {page}: {str(e)}")
            break

    return all_listings 