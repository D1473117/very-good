import random
from app.models.base import get_db_connection

def init_db():
    conn = get_db_connection()
    
    # We only create tables if they do not exist yet, preserving existing user data.
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Restaurant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id TEXT,
            name TEXT NOT NULL,
            address TEXT,
            rating REAL,
            user_ratings_total INTEGER,
            open_hours TEXT,
            photo_url TEXT,
            latitude REAL,
            longitude REAL,
            price_level INTEGER,
            category TEXT,
            signature TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS Favorite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES User (id),
            FOREIGN KEY (restaurant_id) REFERENCES Restaurant (id),
            UNIQUE(user_id, restaurant_id)
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES User (id),
            FOREIGN KEY (restaurant_id) REFERENCES Restaurant (id)
        )
    ''')
    
    # Insert richer dummy data
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Restaurant')
    count = cursor.fetchone()[0]
    if count == 0:
        dummy_data = [
            ('1', '麥當勞', '台北市信義區信義路五段7號', 4.1, 1500, '24 小時營業', 'https://images.unsplash.com/photo-1619881589316-56c7f9e6b587', 25.033964, 121.564468, 1, '速食', '大麥克、黃金薯條、麥克雞塊'),
            ('2', '鼎泰豐', '台北市信義區市府路45號', 4.6, 3200, '11:00 - 21:00', 'https://images.unsplash.com/photo-1496116218417-1a781b1c416c', 25.033964, 121.564468, 3, '中式/水餃', '招牌小籠包、排骨蛋炒飯、紅油抄手'),
            ('3', '一蘭拉麵', '台北市信義區松仁路97號', 4.4, 8500, '24 小時營業', 'https://images.unsplash.com/photo-1552611052-33e04de081de', 25.033964, 121.564468, 2, '日式', '天然豚骨拉麵、釜醬汁叉燒飯、半熟鹽味蛋'),
            ('4', '海底撈火鍋', '台北市信義區松壽路12號', 4.8, 4100, '11:00 - 04:00', 'https://images.unsplash.com/photo-1511690656952-34342bb7c2f2', 25.033964, 121.564468, 3, '火鍋', '招牌麻辣火鍋、撈派滑牛肉、現做手拉甩麵'),
            ('5', '五花馬水餃館', '台北市信義區莊敬路325號', 3.9, 450, '11:00 - 20:30', 'https://images.unsplash.com/photo-1541592106381-b31e9677c0e5', 25.033964, 121.564468, 1, '中式/水餃', '高麗菜手工水餃、蔥油餅、溫熱小米粥'),
            ('6', '壽司郎', '台北市中正區館前路8號', 4.3, 2800, '11:00 - 22:00', 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c', 25.046255, 121.515286, 2, '日式', '極上生鮭魚、特選鮪魚大腹、炙燒起司鮮蝦'),
            ('7', '石二鍋', '台北市大安區信義路二段222號', 4.2, 1900, '11:30 - 22:30', 'https://images.unsplash.com/photo-1547928576-a4a3323dce9a', 25.033621, 121.530321, 1, '火鍋', '經典石頭鍋、上等雪花牛肉、檸檬冬瓜冰沙'),
            ('8', '肯德基', '台北市信義區忠孝東路五段22號', 3.8, 800, '07:00 - 23:00', 'https://images.unsplash.com/photo-1513639776629-7b61b0ac2313', 25.041212, 121.565431, 1, '速食', '咔啦脆雞、原味葡式蛋撻、義式紙包雞'),
            ('9', '乾杯燒肉居酒屋', '台北市大安區敦化南路一段236巷17號', 4.5, 3400, '17:00 - 23:00', 'https://images.unsplash.com/photo-1504674900247-0877df9cc836', 25.038129, 121.549234, 3, '日式', '鹽蔥厚切牛舌、椒鹽霜降豬肉、現切澳洲和牛肋眼'),
        ]
        cursor.executemany('''
            INSERT INTO Restaurant (place_id, name, address, rating, user_ratings_total, open_hours, photo_url, latitude, longitude, price_level, category, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', dummy_data)
        conn.commit()
    
    conn.close()

def get_random_restaurant(category=None, price_level=None, min_rating=None, user_id=None):
    from app.models.favorite import is_user_favorited  # Prevent circular import
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM Restaurant WHERE 1=1'
    params = []
    
    if category and category != 'all':
        query += ' AND category = ?'
        params.append(category)
        
    if price_level and price_level != 'all':
        query += ' AND price_level = ?'
        params.append(int(price_level))
        
    if min_rating and min_rating != 'all':
        query += ' AND rating >= ?'
        params.append(float(min_rating))
        
    cursor.execute(query, params)
    restaurants = cursor.fetchall()
    conn.close()
    
    if restaurants:
        selected = dict(random.choice(restaurants))
        if user_id:
            # Check if this restaurant is favorited by the user
            selected['is_favorited'] = is_user_favorited(user_id, selected['id'])
        else:
            selected['is_favorited'] = False
        return selected
    return None

def create_restaurant(data):
    """
    新增一筆餐廳記錄。
    
    :param data: 包含餐廳欄位值的字典 (name 必填)
    :return: 新增成功的餐廳 ID，若失敗則回傳 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Restaurant (place_id, name, address, rating, user_ratings_total, open_hours, photo_url, latitude, longitude, price_level, category, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('place_id'),
            data['name'],
            data.get('address'),
            data.get('rating'),
            data.get('user_ratings_total'),
            data.get('open_hours'),
            data.get('photo_url'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('price_level'),
            data.get('category'),
            data.get('signature')
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"Error creating restaurant: {e}")
        return None

def get_all_restaurants():
    """
    取得所有餐廳記錄。
    
    :return: 餐廳字典列表
    """
    try:
        conn = get_db_connection()
        restaurants = conn.execute('SELECT * FROM Restaurant').fetchall()
        conn.close()
        return [dict(r) for r in restaurants]
    except Exception as e:
        print(f"Error getting all restaurants: {e}")
        return []

def get_restaurant_by_id(restaurant_id):
    """
    根據 ID 取得單筆餐廳記錄。
    
    :param restaurant_id: 餐廳主鍵 ID
    :return: 餐廳字典，若不存在則回傳 None
    """
    try:
        conn = get_db_connection()
        restaurant = conn.execute('SELECT * FROM Restaurant WHERE id = ?', (restaurant_id,)).fetchone()
        conn.close()
        return dict(restaurant) if restaurant else None
    except Exception as e:
        print(f"Error getting restaurant by id {restaurant_id}: {e}")
        return None

def update_restaurant(restaurant_id, data):
    """
    更新指定 ID 的餐廳記錄。
    
    :param restaurant_id: 餐廳主鍵 ID
    :param data: 包含欲更新欄位值的字典
    :return: 更新是否成功 (True/False)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        params = []
        for key in ['place_id', 'name', 'address', 'rating', 'user_ratings_total', 'open_hours', 'photo_url', 'latitude', 'longitude', 'price_level', 'category', 'signature']:
            if key in data:
                fields.append(f"{key} = ?")
                params.append(data[key])
                
        if not fields:
            conn.close()
            return False
            
        params.append(restaurant_id)
        query = f"UPDATE Restaurant SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, params)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error updating restaurant {restaurant_id}: {e}")
        return False

def delete_restaurant(restaurant_id):
    """
    刪除指定 ID 的餐廳記錄。
    
    :param restaurant_id: 餐廳主鍵 ID
    :return: 刪除是否成功 (True/False)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Restaurant WHERE id = ?', (restaurant_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error deleting restaurant {restaurant_id}: {e}")
        return False

