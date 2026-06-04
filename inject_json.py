import json
import random
from app import create_app, db
from app.models.restaurant import Restaurant

app = create_app()

def import_restaurants():
    with app.app_context():
        with open('database/restaurants_seed.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Found {len(data)} restaurants in JSON.")
        
        # Get existing names to avoid duplicates
        existing = {r.name for r in Restaurant.query.all()}
        
        new_restaurants = []
        for item in data:
            if item['name'] in existing:
                continue
                
            # Parse price level from price_range
            price_str = item.get('price_range', '')
            price_level = 1
            if '$' in price_str:
                if '500' in price_str or '1000' in price_str:
                    price_level = 3
                elif '200' in price_str or '300' in price_str:
                    price_level = 2
            
            # Generate a random distance between 100m and 5000m for demonstration
            # since our system filters by distance.
            distance = random.randint(100, 5000)
            
            r = Restaurant(
                name=item['name'],
                category=item.get('category', '綜合'),
                rating=float(item.get('rating', 0.0) or 0.0),
                address=item.get('address', '無地址'),
                price_level=price_level,
                distance=distance,
                lat=item.get('latitude'),
                lng=item.get('longitude')
            )
            new_restaurants.append(r)
            existing.add(item['name'])
            
        if new_restaurants:
            print(f"Inserting {len(new_restaurants)} new restaurants...")
            db.session.bulk_save_objects(new_restaurants)
            db.session.commit()
            print("Successfully injected!")
        else:
            print("All restaurants already exist.")

if __name__ == '__main__':
    import_restaurants()
