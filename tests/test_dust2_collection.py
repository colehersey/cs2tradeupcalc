#!/usr/bin/env python3
"""
Test script to gather pricing data for Dust 2 Collection weapons
"""

import sys
import os

# Add src to path for imports (go up one directory from tests to root, then to src)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data.market_api import CSFloatAPI
from data.collections_database import get_dust2_weapons_for_testing, CollectionsDatabase

def test_weapon_search(api, weapon_name, max_attempts=3):
    """Test different search strategies for a weapon"""

    print(f"\n=== Testing: {weapon_name} ===")

    # Strategy 1: Exact match
    listings = api.get_skin_listings(weapon_name, limit=3)
    if listings:
        print(f"OK Found {len(listings)} listings with exact match")
        return listings

    # Strategy 2: Base weapon name only
    base_weapon = weapon_name.split('|')[0].strip()
    print(f"Trying base weapon: {base_weapon}")
    listings = api.get_skin_listings(base_weapon, limit=5)
    if listings:
        # Filter for our specific skin
        filtered = [l for l in listings if weapon_name.lower() in l.get('item', {}).get('market_hash_name', '').lower()]
        if filtered:
            print(f"OK Found {len(filtered)} filtered listings")
            return filtered[:3]
        else:
            print(f"Found {len(listings)} listings but none match our skin")
            return listings[:2]  # Return some for structure analysis

    # Strategy 3: Just the skin name
    if '|' in weapon_name:
        skin_part = weapon_name.split('|')[1].strip().split('(')[0].strip()
        print(f"Trying skin name: {skin_part}")
        listings = api.get_skin_listings(skin_part, limit=3)
        if listings:
            print(f"Found {len(listings)} listings with skin name")
            return listings

    print("No listings found with any strategy")
    return []

def main():
    print("=== Testing Dust 2 Collection Weapon Data Gathering ===")

    try:
        # Initialize API
        api = CSFloatAPI()
        db = CollectionsDatabase()

        # Test API connection
        success, message = api.test_connection()
        if not success:
            print(f"API connection failed: {message}")
            return

        print(f"OK API connected successfully")

        # Get Dust 2 collection test weapons
        test_weapons = get_dust2_weapons_for_testing()
        print(f"\nTesting {len(test_weapons)} Dust 2 weapons...")

        successful_weapons = []
        failed_weapons = []

        # Test each weapon
        for i, weapon_data in enumerate(test_weapons[:8]):  # Limit to first 8 for testing
            weapon_name = weapon_data["name"]

            try:
                listings = test_weapon_search(api, weapon_name)

                if listings:
                    # Analyze the first listing
                    first_listing = listings[0]
                    item = first_listing.get('item', {})

                    print(f"  Price: ${first_listing.get('price', 0)/100:.2f}")
                    print(f"  Type: {item.get('type', 'unknown')}")
                    print(f"  Float: {item.get('float_value', 'missing')}")
                    print(f"  Collection: {item.get('collection', 'missing')}")
                    print(f"  Rarity: {item.get('rarity_name', item.get('rarity', 'missing'))}")
                    print(f"  Full name: {item.get('market_hash_name', 'missing')}")

                    # Convert to our SkinData format
                    try:
                        skin_data = api.convert_to_skin_data(first_listing)
                        print(f"  Successfully converted to SkinData")
                        successful_weapons.append({
                            'weapon': weapon_name,
                            'data': skin_data,
                            'raw_item': item
                        })
                    except Exception as e:
                        print(f"  Conversion error: {e}")
                        failed_weapons.append(weapon_name)
                else:
                    failed_weapons.append(weapon_name)

            except Exception as e:
                print(f"  Error: {e}")
                failed_weapons.append(weapon_name)

        # Summary
        print(f"\n=== SUMMARY ===")
        print(f"Successful: {len(successful_weapons)}")
        print(f"Failed: {len(failed_weapons)}")

        if successful_weapons:
            print(f"\n=== SUCCESSFUL WEAPONS ===")
            for weapon in successful_weapons:
                data = weapon['data']
                print(f"- {data.market_hash_name}: ${data.price_cents/100:.2f}")
                print(f"  Float: {data.float_value}, Collection: {data.collection}")

        if failed_weapons:
            print(f"\n=== FAILED WEAPONS ===")
            for weapon in failed_weapons:
                print(f"- {weapon}")

        # Test collection-based search
        print(f"\n=== Testing Collection-Based Search ===")
        collection_listings = api.get_collection_skins("Dust 2 Collection", limit=10)
        print(f"Direct collection search returned: {len(collection_listings)} items")

        if collection_listings:
            print("Sample items from collection search:")
            for listing in collection_listings[:3]:
                item = listing.get('item', {})
                print(f"- {item.get('market_hash_name', 'Unknown')}")
                print(f"  Collection: {item.get('collection', 'Missing')}")
                print(f"  Type: {item.get('type', 'Missing')}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()