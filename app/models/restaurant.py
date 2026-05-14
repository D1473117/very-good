from app.models.database import get_db_connection
import random
import math

def get_all_restaurants():
    conn = get_db_connection()
    restaurants = conn.execute('SELECT * FROM restaurants').fetchall()
    conn.close()
    return [dict(row) for row in restaurants]

def recommend_restaurant(user_lat, user_lng, max_distance_km=5, budget_level=None):
    restaurants = get_all_restaurants()
    filtered = []
    
    for r in restaurants:
        if budget_level and r['budget_level'] > budget_level:
            continue
            
        # 簡單計算距離 (非精確計算，僅為 MVP 示範)
        # 1度經緯度約等於 111 公里
        if user_lat is not None and user_lng is not None:
            dist = math.sqrt((r['lat'] - user_lat)**2 + (r['lng'] - user_lng)**2) * 111
            if dist <= max_distance_km:
                filtered.append(r)
        else:
            filtered.append(r)
            
    if not filtered:
        return None
        
    return random.choice(filtered)
