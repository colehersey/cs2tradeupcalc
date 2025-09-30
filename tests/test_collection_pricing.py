#!/usr/bin/env python3
"""
Test script to collect pricing data for Dust 2 Collection
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.collection_pricer import CollectionPricer

def main():
    print("=== CS2 Collection Price Data Collector ===")
    print("Starting with Dust 2 Collection for trade-up calculator validation")

    try:
        # Initialize the pricer
        pricer = CollectionPricer("Dust 2 Collection")

        # Collect price data (start with small sample size for testing)
        print("\nCollecting price data...")
        collection_data = pricer.fetch_collection_data(sample_size=5)

        # Print summary
        pricer.print_collection_summary()

        # Test getting specific prices
        print("\n=== Testing Price Retrieval ===")
        test_weapon = "AK-47 | Safari Mesh"
        test_wear = "Field-Tested"

        price = pricer.get_weapon_price(test_weapon, test_wear)
        if price > 0:
            print(f"{test_weapon} ({test_wear}): ${price/100:.2f}")
        else:
            print(f"No price data found for {test_weapon} ({test_wear})")

        print(f"\nData saved to: {pricer.data_file}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()