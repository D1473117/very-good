from app.models.database import get_db_connection
import random
import math

# ==========================================================================
# 1. 實作技能要求：標準 CRUD 函式 (Dictionary-based)
# ==========================================================================

def create(data):
    """
    新增一筆餐廳記錄。
    
    Args:
        data (dict): 包含餐廳欄位鍵值的字典，欄位：name, category, lat, lng, rating, budget_level, google_maps_url, is_custom, session_id
        
    Returns:
        int: 新增成功後產生的餐廳 ID，若失敗回傳 None。
    """
    conn = get_db_connection()
    new_id = None
    try:
        cursor = conn.execute(
            '''INSERT INTO restaurants 
               (name, category, lat, lng, rating, budget_level, google_maps_url, is_custom, session_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data.get('name'),
                data.get('category'),
                data.get('lat', 25.041),
                data.get('lng', 121.536),
                data.get('rating', 5.0),
                data.get('budget_level', 1),
                data.get('google_maps_url'),
                data.get('is_custom', 0),
                data.get('session_id')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        print(f"Error creating restaurant: {e}")
    finally:
        conn.close()
    return new_id

def get_all(session_id=None):
    """
    取得所有餐廳記錄。
    若帶入 session_id，則回傳該用戶可看見的所有餐廳（系統 + 自訂）。
    """
    conn = get_db_connection()
    try:
        if session_id:
            rows = conn.execute(
                'SELECT * FROM restaurants WHERE is_custom = 0 OR (is_custom = 1 AND session_id = ?)',
                (session_id,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT * FROM restaurants').fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting all restaurants: {e}")
        return []
    finally:
        conn.close()

def get_by_id(restaurant_id):
    """
    取得單筆餐廳記錄。
    """
    conn = get_db_connection()
    try:
        row = conn.execute('SELECT * FROM restaurants WHERE id = ?', (restaurant_id,)).fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error getting restaurant by id: {e}")
        return None
    finally:
        conn.close()

def update(restaurant_id, data):
    """
    更新餐廳記錄。
    """
    conn = get_db_connection()
    try:
        conn.execute(
            '''UPDATE restaurants 
               SET name = ?, category = ?, lat = ?, lng = ?, rating = ?, budget_level = ?, google_maps_url = ?, is_custom = ?, session_id = ?
               WHERE id = ?''',
            (
                data.get('name'),
                data.get('category'),
                data.get('lat'),
                data.get('lng'),
                data.get('rating'),
                data.get('budget_level'),
                data.get('google_maps_url'),
                data.get('is_custom'),
                data.get('session_id'),
                restaurant_id
            )
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating restaurant: {e}")
        return False
    finally:
        conn.close()

def delete(restaurant_id):
    """
    刪除餐廳記錄。
    """
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM restaurants WHERE id = ?', (restaurant_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting restaurant: {e}")
        return False
    finally:
        conn.close()


# ==========================================================================
# 2. 專案特有：推薦與自訂私房菜核心邏輯
# ==========================================================================

def get_all_restaurants(session_id=None):
    """
    相容方法：獲取所有當前使用者可見的餐廳。
    """
    return get_all(session_id)

def add_custom_restaurant(session_id, name, category, lat, lng, rating=5.0, budget_level=1, google_maps_url=None):
    """
    相容方法：新增自訂私房餐廳至資料庫。
    """
    return create({
        'name': name,
        'category': category,
        'lat': lat,
        'lng': lng,
        'rating': rating,
        'budget_level': budget_level,
        'google_maps_url': google_maps_url,
        'is_custom': 1,
        'session_id': session_id
    })

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    使用 Haversine 公式計算地球表面兩點距離 (公里)，並乘上台灣道路蜿蜒係數 1.4。
    """
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    straight_distance = R * c
    return straight_distance * 1.4

def recommend_restaurant(user_lat, user_lng, max_distance_km=5, budget_level=3, session_id=None, min_rating=0.0, categories_exclude=None, only_favorites=False):
    """
    核心推薦篩選演算法。
    支援預算、評分、飲食避雷針、口袋名單、地理距離篩選以及 Fallback 機制。
    """
    conn = get_db_connection()
    if only_favorites and session_id:
        rows = conn.execute(
            '''SELECT r.* 
               FROM favorites f
               JOIN restaurants r ON f.restaurant_id = r.id
               WHERE f.session_id = ?''',
            (session_id,)
        ).fetchall()
    else:
        if session_id:
            rows = conn.execute(
                'SELECT * FROM restaurants WHERE is_custom = 0 OR (is_custom = 1 AND session_id = ?)',
                (session_id,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT * FROM restaurants WHERE is_custom = 0').fetchall()
    conn.close()
    
    restaurants = [dict(row) for row in rows]
    
    # 步驟 1：預算、最低評分、避雷針標籤篩選
    filtered = []
    exclude_set = set(categories_exclude) if categories_exclude else set()
    
    for r in restaurants:
        # 預算過濾
        if budget_level and r['budget_level'] > budget_level:
            continue
            
        # 最低評分過濾
        rating = r['rating'] if r['rating'] is not None else 5.0
        if rating < min_rating:
            continue
            
        # 飲食避雷針過濾
        if r['category'] in exclude_set:
            continue
            
        filtered.append(r)
        
    if not filtered:
        return None # 沒有符合基礎條件的餐廳
        
    # 步驟 2：距離篩選
    distance_filtered = []
    # 若使用者拒絕定位且未選擇地標，預設使用台北大安中心坐標 (25.041, 121.536) 作為基準
    ref_lat = user_lat if user_lat is not None else 25.041
    ref_lng = user_lng if user_lng is not None else 121.536
    
    for r in filtered:
        dist = calculate_distance(ref_lat, ref_lng, r['lat'], r['lng'])
        if dist <= max_distance_km:
            distance_filtered.append(r)
        
    # 步驟 3：Fallback 備用機制 (若距離篩選無結果，則退回沒有距離限制的篩選結果)
    if not distance_filtered:
        distance_filtered = filtered
        
    if not distance_filtered:
        return None
        
    # 隨機選出一家
    chosen = random.choice(distance_filtered)
    
    # 附帶檢查當前 Session 收藏狀態
    if session_id:
        from app.models.favorite import is_favorite
        chosen['is_favorite'] = is_favorite(session_id, chosen['id'])
    else:
        chosen['is_favorite'] = False
        
    return chosen
