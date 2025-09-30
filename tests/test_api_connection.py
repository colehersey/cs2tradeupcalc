#!/usr/bin/env python3
"""
Simple test script to verify CSFloat API connection
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.market_api import CSFloatAPI

def main():
    print("Testing CSFloat API connection...")

    try:
        # Initialize API client
        api = CSFloatAPI()
        print("OK API client initialized")

        # Test connection
        success, message = api.test_connection()

        if success:
            print(f"OK {message}")

            # Test fetching basic listings without any filters
            print("\n=== Testing basic listings fetch ===")
            print("Fetching general listings (no filters)...")

            # Direct API call to /listings with minimal parameters
            url = f"{api.config.base_url}/listings"
            params = {'limit': 5, 'sort_by': 'lowest_price'}

            response = api.session.get(url, params=params, timeout=10)
            print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                try:
                    listings = response.json()
                    print(f"Raw response type: {type(listings)}")
                    if isinstance(listings, list) and listings:
                        print(f"Found {len(listings)} listings")

                        # Show first listing structure
                        first_listing = listings[0]
                        print(f"First listing keys: {list(first_listing.keys())}")
                        if 'item' in first_listing:
                            item = first_listing['item']
                            print(f"Item keys: {list(item.keys())}")
                            print(f"Sample: {item.get('market_hash_name', 'Unknown')} - ${first_listing.get('price', 0)/100:.2f}")
                    else:
                        print(f"Unexpected response format: {listings}")
                except Exception as e:
                    print(f"JSON parse error: {e}")
                    print(f"Response content length: {len(response.content)}")
                    print(f"Response headers: {dict(response.headers)}")

                    # Safe print of response
                    try:
                        safe_text = response.text.encode('ascii', 'ignore').decode('ascii')[:200]
                        print(f"Raw response (safe): {safe_text}")
                    except:
                        print(f"Raw response bytes: {response.content[:200]}")
            else:
                print(f"API error: {response.status_code} - {response.text[:200]}")

            # Now test the wrapper function
            print("\n=== Testing wrapper function ===")
            listings = api.get_skin_listings("", limit=3)

            if listings:
                print(f"OK Successfully fetched {len(listings)} listings")

                # Debug first listing structure
                first_listing = listings[0]
                print(f"\nListing structure (top level keys): {list(first_listing.keys())}")

                if 'item' in first_listing:
                    print(f"Item structure keys: {list(first_listing['item'].keys())}")

                # Convert and display skin data
                print("\n--- Sample Listings ---")
                for i, listing in enumerate(listings, 1):
                    try:
                        skin_data = api.convert_to_skin_data(listing)
                        print(f"{i}. {skin_data.market_hash_name}")
                        print(f"   Price: ${skin_data.price_cents/100:.2f}")
                        print(f"   Float: {skin_data.float_value:.6f}")
                        print(f"   Collection: {skin_data.collection}")
                        print(f"   Rarity: {skin_data.rarity}")
                        print()
                    except Exception as e:
                        print(f"   ERROR converting listing {i}: {e}")
                        print(f"   Raw listing: {listing}")
                        print()

                # Test with a more common skin
                print("=== Testing with AK-47 | Redline (any condition) ===")
                ak_listings = api.get_skin_listings("AK-47", limit=5)
                if ak_listings:
                    print(f"OK Found {len(ak_listings)} AK-47 listings")
                    for listing in ak_listings[:2]:  # Show first 2
                        skin_data = api.convert_to_skin_data(listing)
                        print(f"- {skin_data.market_hash_name} | ${skin_data.price_cents/100:.2f} | Float: {skin_data.float_value:.4f}")
                else:
                    print("WARNING No AK-47 listings found")
            else:
                print("WARNING No listings returned for AK-47 | Redline (Field-Tested)")

                # Try a broader search
                print("\nTrying broader search for any AK-47...")
                broad_search = api.get_skin_listings("AK-47", limit=3)
                if broad_search:
                    print(f"OK Found {len(broad_search)} AK-47 listings with broader search")
                    for listing in broad_search:
                        skin_data = api.convert_to_skin_data(listing)
                        print(f"- {skin_data.market_hash_name}")
                else:
                    print("WARNING No listings found even with broader search")

        else:
            print(f"ERROR {message}")
            print("\nTroubleshooting tips:")
            print("1. Check that CSFLOAT_API_KEY is set in your .env file")
            print("2. Verify your API key is correct at https://csfloat.com/profile (Developer tab)")
            print("3. Make sure your API key has the correct permissions")

    except Exception as e:
        print(f"ERROR EXCEPTION: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main()