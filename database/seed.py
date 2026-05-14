import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.database import get_db_connection, init_db

def seed_data():
    init_db()
    conn = get_db_connection()
    restaurants = [
        ('巷口麵店', '麵食', 25.041, 121.536, 4.2, 1, 'https://maps.google.com/?q=巷口麵店'),
        ('豪華牛排館', '西式', 25.042, 121.537, 4.8, 3, 'https://maps.google.com/?q=豪華牛排館'),
        ('大汗麻辣鍋', '火鍋', 25.040, 121.535, 4.5, 2, 'https://maps.google.com/?q=大汗麻辣鍋'),
        ('阿明肉燥飯', '小吃', 25.043, 121.538, 4.0, 1, 'https://maps.google.com/?q=阿明肉燥飯'),
        ('日式拉麵屋', '日式', 25.039, 121.534, 4.3, 2, 'https://maps.google.com/?q=日式拉麵屋'),
        ('素食自助餐', '素食', 25.045, 121.530, 4.1, 1, 'https://maps.google.com/?q=素食自助餐'),
        ('星光餐酒館', '餐酒館', 25.035, 121.540, 4.6, 3, 'https://maps.google.com/?q=星光餐酒館')
    ]
    
    conn.executemany(
        'INSERT INTO restaurants (name, category, lat, lng, rating, budget_level, google_maps_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
        restaurants
    )
    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
