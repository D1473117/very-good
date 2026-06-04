import urllib.request
import urllib.parse
import json
from app import create_app, db
from app.models.restaurant import Restaurant

def fetch_fengchia_restaurants():
    print("Fetching restaurants around Fengchia (10km radius)...")
    query = """
    [out:json];
    (
      node(around:10000, 24.179, 120.646)["amenity"="restaurant"];
      node(around:10000, 24.179, 120.646)["amenity"="cafe"];
      node(around:10000, 24.179, 120.646)["amenity"="fast_food"];
      node(around:10000, 24.179, 120.646)["amenity"="food_court"];
    );
    out body;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    
    data_encoded = urllib.parse.urlencode({'data': query}).encode('utf-8')
    req = urllib.request.Request(url, data=data_encoded, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        elements = data.get('elements', [])
        print(f"Found {len(elements)} real places from OpenStreetMap!")
        
        app = create_app()
        with app.app_context():
            added_count = 0
            for el in elements:
                tags = el.get('tags', {})
                name = tags.get('name') or tags.get('name:zh') or tags.get('name:en')
                
                if not name:
                    continue
                    
                # Skip if already exists to prevent duplicates
                if Restaurant.query.filter_by(name=name).first():
                    continue
                    
                cuisine = tags.get('cuisine', '綜合料理')
                # Translate some common cuisines
                cuisine_map = {
                    'japanese': '日式料理',
                    'chinese': '中式料理',
                    'taiwanese': '台灣小吃',
                    'italian': '義式料理',
                    'pizza': '披薩',
                    'burger': '漢堡',
                    'coffee_shop': '咖啡廳',
                    'cafe': '咖啡廳',
                    'noodle': '麵食',
                    'korean': '韓式料理'
                }
                cuisine = cuisine_map.get(cuisine.lower(), cuisine.capitalize())
                
                price_level = 2 # default medium
                price_str = tags.get('price_level', '')
                if price_str == '1': price_level = 1
                elif price_str == '2': price_level = 2
                elif price_str == '3': price_level = 3
                
                res = Restaurant(
                    name=name,
                    description=f"{cuisine} | 位於台中市",
                    price_level=price_level,
                    rating=4.0, # default good rating
                    image_url=None
                )
                db.session.add(res)
                added_count += 1
                
            db.session.commit()
            print(f"Successfully added {added_count} NEW restaurants to the database!")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == '__main__':
    fetch_fengchia_restaurants()
