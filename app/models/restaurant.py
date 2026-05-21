from app.models.database import get_db_connection
import random
import math

def get_all_restaurants(session_id=None):
    conn = get_db_connection()
    if session_id:
        restaurants = conn.execute(
            'SELECT * FROM restaurants WHERE is_custom = 0 OR (is_custom = 1 AND session_id = ?)',
            (session_id,)
        ).fetchall()
    else:
        restaurants = conn.execute('SELECT * FROM restaurants WHERE is_custom = 0').fetchall()
    conn.close()
    return [dict(row) for row in restaurants]

def add_custom_restaurant(session_id, name, category, lat, lng, rating=5.0, budget_level=1, google_maps_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''INSERT INTO restaurants 
               (name, category, lat, lng, rating, budget_level, google_maps_url, is_custom, session_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)''',
            (name, category, lat, lng, rating, budget_level, google_maps_url, session_id)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return new_id
    except Exception as e:
        print(f"Error adding custom restaurant: {e}")
        return None
    finally:
        conn.close()

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

def recommend_restaurant(user_lat, user_lng, max_distance_km=5, budget_level=3, 
                         categories_exclude=None, categories_only=None, min_rating=0.0, 
                         only_favorites=False, session_id=None):
    conn = get_db_connection()
    
    # 步驟 1：依收藏篩選或常規查詢
    if only_favorites and session_id:
        # 只從收藏中抽取
        query = '''
            SELECT r.* FROM restaurants r
            JOIN favorites f ON r.id = f.restaurant_id
            WHERE f.session_id = ? AND (r.is_custom = 0 OR (r.is_custom = 1 AND r.session_id = ?))
        '''
        rows = conn.execute(query, (session_id, session_id)).fetchall()
    else:
        # 全域或 session 自訂餐廳
        if session_id:
            query = 'SELECT * FROM restaurants WHERE is_custom = 0 OR (is_custom = 1 AND session_id = ?)'
            rows = conn.execute(query, (session_id,)).fetchall()
        else:
            query = 'SELECT * FROM restaurants WHERE is_custom = 0'
            rows = conn.execute(query).fetchall()
            
    conn.close()
    restaurants = [dict(row) for row in rows]
    
    # 步驟 2：進階過濾（排除分類、指定分類、最低評分、預算）
    filtered = []
    for r in restaurants:
        # 1. 預算過濾
        if budget_level and r['budget_level'] > budget_level:
            continue
            
        # 2. 飲食避雷針：排除特定分類
        if categories_exclude and r['category'] in categories_exclude:
            continue
            
        # 3. 指定分類
        if categories_only and r['category'] not in categories_only:
            continue
            
        # 4. 最低評分
        rating_val = r['rating'] if r['rating'] is not None else 0.0
        if rating_val < min_rating:
            continue
            
        filtered.append(r)
        
    if not filtered:
        return None # 沒有符合條件的餐廳
        
    # 步驟 3：再用距離篩選
    distance_filtered = []
    if user_lat is not None and user_lng is not None:
        for r in filtered:
            dist = calculate_distance(user_lat, user_lng, r['lat'], r['lng'])
            if dist <= max_distance_km:
                distance_filtered.append(r)
    else:
        distance_filtered = filtered
        
    # 步驟 4：Fallback 機制 (若距離篩選無結果，則退回沒有距離限制的篩選結果)
    if not distance_filtered:
        distance_filtered = filtered
        
    if not distance_filtered:
        return None
        
    return random.choice(distance_filtered)
