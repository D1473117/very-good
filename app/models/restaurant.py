from app.models.database import get_db_connection
import random
import math

def get_all_restaurants():
    conn = get_db_connection()
    restaurants = conn.execute('SELECT * FROM restaurants').fetchall()
    conn.close()
    return [dict(row) for row in restaurants]

def calculate_distance(lat1, lon1, lat2, lon2):
    # 使用 Haversine 公式計算地球表面兩點距離 (公里)
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    straight_distance = R * c
    
    # 由於直線距離 (鳥飛距離) 往往比實際道路距離短，
    # 在台灣市區加上約 1.3 ~ 1.4 倍的道路蜿蜒常數 (Route factor)，能更貼近實際騎車距離。
    return straight_distance * 1.4

def recommend_restaurant(user_lat, user_lng, max_distance_km=5, budget_level=None):
    restaurants = get_all_restaurants()
    
    # 步驟 1：先用預算篩選
    budget_filtered = []
    for r in restaurants:
        if budget_level and r['budget_level'] > budget_level:
            continue
        budget_filtered.append(r)
        
    if not budget_filtered:
        return None # 連符合預算的都沒有
        
    # 步驟 2：再用距離篩選
    distance_filtered = []
    if user_lat is not None and user_lng is not None:
        for r in budget_filtered:
            dist = calculate_distance(user_lat, user_lng, r['lat'], r['lng'])
            if dist <= max_distance_km:
                distance_filtered.append(r)
    else:
        distance_filtered = budget_filtered
        
    # 步驟 3：Fallback 機制
    if not distance_filtered:
        distance_filtered = budget_filtered
        
    return random.choice(distance_filtered)
