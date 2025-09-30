#!/usr/bin/env python3
"""
Comprehensive Dust 2 Collection pricing data gathering
Tests all weapons across all wear tiers to match the provided pricing data
"""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data.market_api import CSFloatAPI
from data.collections_database import DUST2_COLLECTION, WEAR_CONDITIONS

def gather_weapon_pricing(api, weapon_data, sample_size=10):
    """
    Gather comprehensive pricing data for a weapon across all wear tiers

    Returns:
        Dict with wear tier -> {min_price, max_price, avg_price, sample_count}
    """
    weapon_name = weapon_data["full_name"]
    pricing_data = {}

    print(f"\n=== {weapon_name} ===")

    for wear in WEAR_CONDITIONS:
        full_name = f"{weapon_name} ({wear})"

        try:
            # Get multiple listings to calculate price range
            listings = api.get_skin_listings(full_name, limit=sample_size, sort_by="lowest_price")

            if listings:
                prices = []
                valid_listings = 0

                for listing in listings:
                    price = listing.get('price', 0)
                    item = listing.get('item', {})

                    # Verify this is actually from Dust 2 Collection
                    collection = item.get('collection', '')
                    item_name = item.get('market_hash_name', '')

                    if price > 0 and ('dust' in collection.lower() or full_name.lower() in item_name.lower()):
                        prices.append(price)
                        valid_listings += 1

                if prices:
                    min_price = min(prices) / 100  # Convert cents to dollars
                    max_price = max(prices) / 100
                    avg_price = sum(prices) / len(prices) / 100

                    pricing_data[wear] = {
                        'min_price': min_price,
                        'max_price': max_price,
                        'avg_price': avg_price,
                        'sample_count': len(prices),
                        'total_listings': len(listings)
                    }

                    print(f"  {wear}: ${min_price:.2f} - ${max_price:.2f} (avg: ${avg_price:.2f}, {len(prices)} samples)")
                else:
                    print(f"  {wear}: No valid prices found")
            else:
                print(f"  {wear}: No listings found")

        except Exception as e:
            print(f"  {wear}: Error - {e}")

        # Rate limiting pause
        time.sleep(0.5)

    return pricing_data

def main():
    print("=== Comprehensive Dust 2 Collection Pricing Analysis ===")
    print("Gathering pricing data for all weapons across all wear tiers\n")

    try:
        # Initialize API
        api = CSFloatAPI()

        # Test connection
        success, message = api.test_connection()
        if not success:
            print(f"API connection failed: {message}")
            return

        print(f"API connected successfully")

        # Get all Dust 2 weapons organized by rarity
        dust2_weapons = DUST2_COLLECTION["weapons"]
        all_pricing_data = {}

        # Process each rarity tier
        for rarity, weapons in dust2_weapons.items():
            print(f"\n{'='*50}")
            print(f"RARITY: {rarity}")
            print(f"{'='*50}")

            rarity_data = {}

            for weapon in weapons:
                weapon_pricing = gather_weapon_pricing(api, weapon, sample_size=15)

                if weapon_pricing:
                    rarity_data[weapon["full_name"]] = weapon_pricing

                    # Calculate overall price range for weapon
                    all_prices = []
                    for wear_data in weapon_pricing.values():
                        all_prices.extend([wear_data['min_price'], wear_data['max_price']])

                    if all_prices:
                        overall_min = min(all_prices)
                        overall_max = max(all_prices)
                        print(f"  Overall range: ${overall_min:.2f} to ${overall_max:.2f}")

                # Pause between weapons to be respectful to API
                time.sleep(1)

            all_pricing_data[rarity] = rarity_data

        # Summary Report
        print(f"\n{'='*60}")
        print("DUST 2 COLLECTION PRICING SUMMARY")
        print(f"{'='*60}")

        for rarity, weapons_data in all_pricing_data.items():
            print(f"\n{rarity}:")

            for weapon_name, pricing in weapons_data.items():
                if pricing:
                    # Calculate overall range
                    all_prices = []
                    for wear_data in pricing.values():
                        all_prices.extend([wear_data['min_price'], wear_data['max_price']])

                    if all_prices:
                        overall_min = min(all_prices)
                        overall_max = max(all_prices)
                        print(f"  {weapon_name}")
                        print(f"    from ${overall_min:.2f} to ${overall_max:.2f}")

                        # Show wear tier breakdown
                        for wear, data in pricing.items():
                            print(f"      {wear}: ${data['min_price']:.2f} - ${data['max_price']:.2f} ({data['sample_count']} samples)")
                else:
                    print(f"  {weapon_name}: No pricing data available")

        print(f"\n{'='*60}")
        print("Data collection complete!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()