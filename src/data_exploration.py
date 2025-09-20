from csfloat_api import get_all_listings
import pandas as pd
from tqdm import tqdm

def extract_relevant_fields(listings):
    records = []
    for l in listings:
        item = l.get('item', {})
        records.append({
            'listing_id': l.get('id'),
            'asset_id': item.get('asset_id'),
            'collection': item.get('collection'),
            'rarity': item.get('rarity'),
            'is_stattrak': item.get('is_stattrak'),
            'is_souvenir': item.get('is_souvenir'),
            'float_value': item.get('float_value'),
            'price': l.get('price'),
            'market_hash_name': item.get('market_hash_name'),
            'item_name': item.get('item_name'),
            'wear_name': item.get('wear_name'),
        })
    return records

def main():
    print("Fetching all CSFloat listings...")
    listings = get_all_listings()
    print(f"Fetched {len(listings)} listings.")
    print("Extracting relevant fields...")
    records = extract_relevant_fields(listings)
    df = pd.DataFrame(records)
    print("Grouping by (collection, rarity, is_stattrak, is_souvenir)...")
    group_cols = ['collection', 'rarity', 'is_stattrak', 'is_souvenir']
    grouped = df.groupby(group_cols).size().reset_index(name='count')
    print(grouped.sort_values('count', ascending=False).head(20))

if __name__ == "__main__":
    main() 