"""
Collection Price Data Manager
Fetches and stores average pricing data for a specific CS2 collection
"""

import json
import os
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass
from .market_api import CSFloatAPI

@dataclass
class WeaponPriceData:
    """Price data for a weapon at specific wear tier"""
    avg_price_cents: int
    sample_size: int
    last_updated: str

@dataclass
class WeaponData:
    """Complete weapon data across all wear tiers"""
    name: str
    rarity: str
    wear_data: Dict[str, WeaponPriceData]

class CollectionPricer:
    """Manages price data collection for a specific CS2 collection"""

    # Spectrum Collection weapon data by rarity (more actively traded)
    SPECTRUM_COLLECTION = {
        "Mil-Spec": [
            "CZ75-Auto | Tread Plate",
            "P2000 | Turf",
            "SCAR-20 | Green Marine"
        ],
        "Restricted": [
            "USP-S | Neo-Noir",
            "AK-47 | Phantom Disruptor"
        ],
        "Classified": [
            "M4A1-S | Decimator"
        ],
        "Covert": [
            "AK-47 | Bloodsport"
        ]
    }

    WEAR_TIERS = [
        "Factory New",
        "Minimal Wear",
        "Field-Tested",
        "Well-Worn",
        "Battle-Scarred"
    ]

    def __init__(self, collection_name: str = "Spectrum Collection"):
        self.collection_name = collection_name
        self.api = CSFloatAPI()
        self.data_file = f"data/{collection_name.lower().replace(' ', '_')}_prices.json"

        # Map collection to data
        if collection_name == "Spectrum Collection":
            self.collection_data = self.SPECTRUM_COLLECTION
        else:
            raise ValueError(f"Collection '{collection_name}' not supported yet")

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Load existing data if available
        self.price_data = self._load_existing_data()

    def _load_existing_data(self) -> Dict:
        """Load existing price data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                print(f"Warning: Could not load existing data from {self.data_file}")

        return {}

    def _save_data(self):
        """Save current price data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.price_data, f, indent=2)
            print(f"Price data saved to {self.data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def fetch_weapon_prices(self, weapon_name: str, sample_size: int = 10) -> Dict[str, WeaponPriceData]:
        """
        Fetch price data for a weapon across all wear tiers

        Args:
            weapon_name: Full weapon name (e.g., "AK-47 | Safari Mesh")
            sample_size: Number of listings to sample for average

        Returns:
            Dict mapping wear tier to price data
        """
        weapon_prices = {}

        print(f"\nFetching prices for: {weapon_name}")

        for wear in self.WEAR_TIERS:
            try:
                full_name = f"{weapon_name} ({wear})"
                print(f"  Checking {wear}...")

                # Get listings for this weapon + wear combination
                listings = self.api.get_skin_listings(full_name, limit=sample_size, sort_by="lowest_price")

                if listings:
                    # Calculate average price from listings
                    prices = []
                    for listing in listings:
                        price = listing.get('price', 0)
                        if price > 0:
                            prices.append(price)

                    if prices:
                        avg_price = int(sum(prices) / len(prices))
                        weapon_prices[wear] = WeaponPriceData(
                            avg_price_cents=avg_price,
                            sample_size=len(prices),
                            last_updated=datetime.now().isoformat()
                        )
                        print(f"    Found {len(prices)} listings, avg: ${avg_price/100:.2f}")
                    else:
                        print(f"    No valid prices found")
                else:
                    print(f"    No listings found")

            except Exception as e:
                print(f"    Error fetching {wear}: {e}")

        return weapon_prices

    def fetch_collection_data(self, sample_size: int = 10):
        """
        Fetch price data for entire collection

        Args:
            sample_size: Number of listings to sample per weapon/wear combination
        """
        print(f"=== Fetching {self.collection_name} Price Data ===")

        collection_data = {
            "collection_name": self.collection_name,
            "last_updated": datetime.now().isoformat(),
            "weapons": {}
        }

        for rarity, weapons in self.collection_data.items():
            print(f"\n--- {rarity} ---")

            for weapon in weapons:
                # Fetch price data for this weapon
                weapon_prices = self.fetch_weapon_prices(weapon, sample_size)

                # Store the data
                collection_data["weapons"][weapon] = {
                    "rarity": rarity,
                    "wear_data": {}
                }

                # Convert WeaponPriceData to dict for JSON storage
                for wear, price_data in weapon_prices.items():
                    collection_data["weapons"][weapon]["wear_data"][wear] = {
                        "avg_price_cents": price_data.avg_price_cents,
                        "sample_size": price_data.sample_size,
                        "last_updated": price_data.last_updated
                    }

        # Store the collected data
        self.price_data = collection_data
        self._save_data()

        return collection_data

    def get_weapon_price(self, weapon_name: str, wear_tier: str) -> int:
        """
        Get cached price for a specific weapon/wear combination

        Returns:
            Price in cents, or 0 if not found
        """
        if weapon_name in self.price_data.get("weapons", {}):
            wear_data = self.price_data["weapons"][weapon_name].get("wear_data", {})
            if wear_tier in wear_data:
                return wear_data[wear_tier]["avg_price_cents"]
        return 0

    def print_collection_summary(self):
        """Print a summary of collected price data"""
        if not self.price_data.get("weapons"):
            print("No price data available")
            return

        print(f"\n=== {self.collection_name} Price Summary ===")

        for rarity, weapons in self.collection_data.items():
            print(f"\n{rarity}:")

            for weapon in weapons:
                if weapon in self.price_data["weapons"]:
                    wear_data = self.price_data["weapons"][weapon]["wear_data"]
                    print(f"  {weapon}:")

                    for wear in self.WEAR_TIERS:
                        if wear in wear_data:
                            price_cents = wear_data[wear]["avg_price_cents"]
                            sample_size = wear_data[wear]["sample_size"]
                            print(f"    {wear}: ${price_cents/100:.2f} ({sample_size} samples)")
                        else:
                            print(f"    {wear}: No data")
                else:
                    print(f"  {weapon}: No data collected")