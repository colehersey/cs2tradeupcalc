"""
CS2 Collections Database
Comprehensive mapping of CS2 collections and their weapon skins by rarity tier
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CollectionSkin:
    """Individual skin within a collection"""
    weapon_name: str
    skin_name: str
    full_name: str  # e.g., "AK-47 | Safari Mesh (Field-Tested)"
    rarity: str
    rarity_tier: int  # 1=Industrial, 2=Mil-Spec, 3=Restricted, 4=Classified, 5=Covert

# Dust 2 Collection - Accurate weapon mapping based on CS2 data
DUST2_COLLECTION = {
    "collection_name": "The Dust 2 Collection",
    "active": True,
    "tradeable": True,
    "weapons": {
        "Consumer Grade": [
            {
                "weapon": "G3SG1",
                "skin": "Desert Storm",
                "full_name": "G3SG1 | Desert Storm",
                "rarity_tier": 0
            },
            {
                "weapon": "MP9",
                "skin": "Sand Dashed",
                "full_name": "MP9 | Sand Dashed",
                "rarity_tier": 0
            },
            {
                "weapon": "Nova",
                "skin": "Predator",
                "full_name": "Nova | Predator",
                "rarity_tier": 0
            },
            {
                "weapon": "P250",
                "skin": "Sand Dune",
                "full_name": "P250 | Sand Dune",
                "rarity_tier": 0
            },
            {
                "weapon": "P90",
                "skin": "Sand Spray",
                "full_name": "P90 | Sand Spray",
                "rarity_tier": 0
            },
            {
                "weapon": "SCAR-20",
                "skin": "Sand Mesh",
                "full_name": "SCAR-20 | Sand Mesh",
                "rarity_tier": 0
            }
        ],
        "Industrial Grade": [
            {
                "weapon": "Five-SeveN",
                "skin": "Orange Peel",
                "full_name": "Five-SeveN | Orange Peel",
                "rarity_tier": 1
            },
            {
                "weapon": "MAC-10",
                "skin": "Palm",
                "full_name": "MAC-10 | Palm",
                "rarity_tier": 1
            },
            {
                "weapon": "Sawed-Off",
                "skin": "Snake Camo",
                "full_name": "Sawed-Off | Snake Camo",
                "rarity_tier": 1
            },
            {
                "weapon": "Tec-9",
                "skin": "VariCamo",
                "full_name": "Tec-9 | VariCamo",
                "rarity_tier": 1
            }
        ],
        "Mil-Spec Grade": [
            {
                "weapon": "PP-Bizon",
                "skin": "Brass",
                "full_name": "PP-Bizon | Brass",
                "rarity_tier": 2
            },
            {
                "weapon": "SG 553",
                "skin": "Damascus Steel",
                "full_name": "SG 553 | Damascus Steel",
                "rarity_tier": 2
            }
        ],
        "Restricted": [
            {
                "weapon": "AK-47",
                "skin": "Safari Mesh",
                "full_name": "AK-47 | Safari Mesh",
                "rarity_tier": 3
            },
            {
                "weapon": "M4A1-S",
                "skin": "VariCamo",
                "full_name": "M4A1-S | VariCamo",
                "rarity_tier": 3
            },
            {
                "weapon": "P2000",
                "skin": "Amber Fade",
                "full_name": "P2000 | Amber Fade",
                "rarity_tier": 3
            },
            {
                "weapon": "R8 Revolver",
                "skin": "Amber Fade",
                "full_name": "R8 Revolver | Amber Fade",
                "rarity_tier": 3
            }
        ]
        # Note: No Classified or Covert tiers in Dust 2 Collection
        # R8 Revolver | Amber Fade is the only pink (Restricted) item
    }
}

# Alternative popular collection for testing
MIRAGE_COLLECTION = {
    "collection_name": "Mirage Collection",
    "active": True,
    "tradeable": True,
    "weapons": {
        "Industrial Grade": [
            {
                "weapon": "MP9",
                "skin": "Hot Rod",
                "full_name": "MP9 | Hot Rod",
                "rarity_tier": 1
            },
            {
                "weapon": "MAG-7",
                "skin": "Sand Dune",
                "full_name": "MAG-7 | Sand Dune",
                "rarity_tier": 1
            }
        ],
        "Mil-Spec Grade": [
            {
                "weapon": "P250",
                "skin": "Sand Dune",
                "full_name": "P250 | Sand Dune",
                "rarity_tier": 2
            },
            {
                "weapon": "UMP-45",
                "skin": "Fallout Warning",
                "full_name": "UMP-45 | Fallout Warning",
                "rarity_tier": 2
            }
        ],
        "Restricted": [
            {
                "weapon": "AK-47",
                "skin": "Emerald Pinstripe",
                "full_name": "AK-47 | Emerald Pinstripe",
                "rarity_tier": 3
            },
            {
                "weapon": "M4A1-S",
                "skin": "VariCamo",
                "full_name": "M4A1-S | VariCamo",
                "rarity_tier": 3
            }
        ]
    }
}

# Italy Collection (Popular "filler" collection)
ITALY_COLLECTION = {
    "collection_name": "Italy Collection",
    "active": False,  # Legacy collection
    "tradeable": True,
    "weapons": {
        "Industrial Grade": [
            {
                "weapon": "Tec-9",
                "skin": "Groundwater",
                "full_name": "Tec-9 | Groundwater",
                "rarity_tier": 1
            }
        ],
        "Mil-Spec Grade": [
            {
                "weapon": "Five-SeveN",
                "skin": "Orange Peel",
                "full_name": "Five-SeveN | Orange Peel",
                "rarity_tier": 2
            }
        ],
        "Restricted": [
            {
                "weapon": "Galil AR",
                "skin": "Orange DDPAT",
                "full_name": "Galil AR | Orange DDPAT",
                "rarity_tier": 3
            }
        ]
    }
}

# Wear conditions that apply to all weapons
WEAR_CONDITIONS = [
    "Factory New",
    "Minimal Wear",
    "Field-Tested",
    "Well-Worn",
    "Battle-Scarred"
]

# Rarity hierarchy for tradeup calculations
RARITY_HIERARCHY = [
    "Consumer Grade",      # Cannot be used in tradeups (lowest tier)
    "Industrial Grade",    # Tier 1
    "Mil-Spec Grade",     # Tier 2
    "Restricted",         # Tier 3
    "Classified",         # Tier 4
    "Covert"             # Tier 5 (cannot trade up from this)
]

class CollectionsDatabase:
    """Database manager for CS2 collections and weapon data"""

    def __init__(self):
        self.collections = {
            "Dust 2 Collection": DUST2_COLLECTION,
            "Mirage Collection": MIRAGE_COLLECTION,
            "Italy Collection": ITALY_COLLECTION
        }

    def get_collection(self, collection_name: str) -> Dict:
        """Get collection data by name"""
        return self.collections.get(collection_name, {})

    def get_weapons_by_rarity(self, collection_name: str, rarity: str) -> List[Dict]:
        """Get all weapons of a specific rarity from a collection"""
        collection = self.get_collection(collection_name)
        if not collection:
            return []
        return collection.get("weapons", {}).get(rarity, [])

    def get_tradeup_outcomes(self, collection_name: str, input_rarity: str) -> List[Dict]:
        """
        Get possible tradeup outcomes for given input rarity
        Returns weapons from the next rarity tier up
        """
        try:
            input_tier = RARITY_HIERARCHY.index(input_rarity)
            if input_tier >= len(RARITY_HIERARCHY) - 1:
                return []  # Can't trade up from highest tier

            output_rarity = RARITY_HIERARCHY[input_tier + 1]
            return self.get_weapons_by_rarity(collection_name, output_rarity)

        except ValueError:
            return []  # Invalid rarity

    def generate_weapon_variants(self, weapon_data: Dict) -> List[str]:
        """Generate all wear condition variants for a weapon"""
        base_name = weapon_data["full_name"]
        variants = []

        for wear in WEAR_CONDITIONS:
            full_name = f"{base_name} ({wear})"
            variants.append(full_name)

        return variants

    def get_all_tradeable_collections(self) -> List[str]:
        """Get list of all collections that support tradeups"""
        return [
            name for name, data in self.collections.items()
            if data.get("tradeable", False)
        ]

# Convenience function for external use
def get_dust2_weapons_for_testing():
    """Get Dust 2 collection weapons formatted for API testing"""
    db = CollectionsDatabase()
    dust2 = db.get_collection("Dust 2 Collection")

    test_weapons = []
    for rarity, weapons in dust2["weapons"].items():
        for weapon in weapons:
            # Generate variants for common wear conditions
            for wear in ["Field-Tested", "Minimal Wear"]:
                full_name = f"{weapon['full_name']} ({wear})"
                test_weapons.append({
                    "name": full_name,
                    "rarity": rarity,
                    "tier": weapon["rarity_tier"]
                })

    return test_weapons