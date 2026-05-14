import sqlite3
import random
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'database.db')

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
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
            longitude REAL
        )
    ''')
    
    # Insert dummy data if empty
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Restaurant')
    count = cursor.fetchone()[0]
    if count == 0:
        dummy_data = [
            ('1', '麥當勞', '台北市信義區信義路五段7號', 4.1, 1500, '24 小時營業', 'https://images.unsplash.com/photo-1619881589316-56c7f9e6b587', 25.033964, 121.564468),
            ('2', '鼎泰豐', '台北市信義區市府路45號', 4.6, 3200, '11:00 - 21:00', 'https://images.unsplash.com/photo-1496116218417-1a781b1c416c', 25.033964, 121.564468),
            ('3', '一蘭拉麵', '台北市信義區松仁路97號', 4.4, 8500, '24 小時營業', 'https://images.unsplash.com/photo-1552611052-33e04de081de', 25.033964, 121.564468),
            ('4', '海底撈火鍋', '台北市信義區松壽路12號', 4.8, 4100, '11:00 - 04:00', 'https://images.unsplash.com/photo-1511690656952-34342bb7c2f2', 25.033964, 121.564468),
            ('5', '五花馬水餃館', '台北市信義區莊敬路325號', 3.9, 450, '11:00 - 20:30', 'https://images.unsplash.com/photo-1541592106381-b31e9677c0e5', 25.033964, 121.564468),
        ]
        cursor.executemany('''
            INSERT INTO Restaurant (place_id, name, address, rating, user_ratings_total, open_hours, photo_url, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', dummy_data)
        conn.commit()
    
    conn.close()

def get_random_restaurant():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Restaurant')
    restaurants = cursor.fetchall()
    conn.close()
    
    if restaurants:
        return dict(random.choice(restaurants))
    return None
