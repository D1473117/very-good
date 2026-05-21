import sqlite3
import random
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'database.db')

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # We drop and recreate tables to ensure smooth schema upgrade in local development.
    # To preserve user data in production we would run migration scripts, but for local MVP,
    # recreating table ensures all column changes are correctly reflected.
    conn.execute('DROP TABLE IF EXISTS Restaurant')
    
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

# ----------------- User Model Functions -----------------
def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO User (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Username already exists

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def check_user_credentials(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

# ----------------- Favorite Model Functions -----------------
def toggle_favorite(user_id, restaurant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if already favorited
    fav = cursor.execute('SELECT * FROM Favorite WHERE user_id = ? AND restaurant_id = ?', 
                         (user_id, restaurant_id)).fetchone()
    
    is_fav = False
    if fav:
        cursor.execute('DELETE FROM Favorite WHERE user_id = ? AND restaurant_id = ?', 
                       (user_id, restaurant_id))
    else:
        cursor.execute('INSERT INTO Favorite (user_id, restaurant_id) VALUES (?, ?)', 
                       (user_id, restaurant_id))
        is_fav = True
        
    conn.commit()
    conn.close()
    return is_fav

def is_user_favorited(user_id, restaurant_id):
    if not user_id:
        return False
    conn = get_db_connection()
    fav = conn.execute('SELECT 1 FROM Favorite WHERE user_id = ? AND restaurant_id = ?', 
                       (user_id, restaurant_id)).fetchone()
    conn.close()
    return fav is not None

def get_user_favorites(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Join with Restaurant to get restaurant details
    favorites = cursor.execute('''
        SELECT r.* FROM Restaurant r
        JOIN Favorite f ON r.id = f.restaurant_id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(f) for f in favorites]

# ----------------- Review Model Functions -----------------
def add_review(user_id, restaurant_id, rating, comment):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Review (user_id, restaurant_id, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (user_id, restaurant_id, rating, comment))
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id

def get_restaurant_reviews(restaurant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    reviews = cursor.execute('''
        SELECT rv.*, u.username FROM Review rv
        JOIN User u ON rv.user_id = u.id
        WHERE rv.restaurant_id = ?
        ORDER BY rv.created_at DESC
    ''', (restaurant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in reviews]

def get_user_reviews(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    reviews = cursor.execute('''
        SELECT rv.*, r.name as restaurant_name, r.photo_url FROM Review rv
        JOIN Restaurant r ON rv.restaurant_id = r.id
        WHERE rv.user_id = ?
        ORDER BY rv.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in reviews]

def delete_review(review_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ensure the review belongs to the user
    cursor.execute('DELETE FROM Review WHERE id = ? AND user_id = ?', (review_id, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

# ----------------- Recommendation Model Functions -----------------
def get_random_restaurant(category=None, price_level=None, min_rating=None, user_id=None):
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

def get_random_favorite(user_id):
    favorites = get_user_favorites(user_id)
    if favorites:
        selected = random.choice(favorites)
        selected['is_favorited'] = True  # It is definitely favorited since it is drawn from favorites
        return selected
    return None
