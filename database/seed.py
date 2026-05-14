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
        ('星光餐酒館', '餐酒館', 25.035, 121.540, 4.6, 3, 'https://maps.google.com/?q=星光餐酒館'),
        ('阿宗麵線', '小吃', 25.043, 121.507, 4.2, 1, 'https://maps.google.com/?q=阿宗麵線'),
        ('無老鍋', '火鍋', 25.048, 121.532, 4.4, 3, 'https://maps.google.com/?q=無老鍋'),
        ('阜杭豆漿', '早餐', 25.044, 121.524, 4.3, 1, 'https://maps.google.com/?q=阜杭豆漿'),
        ('林東芳牛肉麵', '麵食', 25.047, 121.543, 4.4, 2, 'https://maps.google.com/?q=林東芳牛肉麵'),
        ('橘色涮涮屋', '火鍋', 25.040, 121.545, 4.7, 3, 'https://maps.google.com/?q=橘色涮涮屋'),
        ('鬍鬚張魯肉飯', '小吃', 25.056, 121.515, 3.8, 1, 'https://maps.google.com/?q=鬍鬚張魯肉飯'),
        ('藏壽司', '日式', 25.049, 121.520, 4.1, 2, 'https://maps.google.com/?q=藏壽司'),
        ('詹記麻辣火鍋', '火鍋', 25.050, 121.533, 4.5, 3, 'https://maps.google.com/?q=詹記麻辣火鍋'),
        ('金鋒魯肉飯', '小吃', 25.032, 121.518, 4.3, 1, 'https://maps.google.com/?q=金鋒魯肉飯'),
        ('欣葉台菜', '台式', 25.064, 121.523, 4.4, 3, 'https://maps.google.com/?q=欣葉台菜'),
        ('春水堂', '茶館', 25.038, 121.515, 4.2, 2, 'https://maps.google.com/?q=春水堂'),
        ('鼎泰豐', '中式', 25.033, 121.529, 4.7, 3, 'https://maps.google.com/?q=鼎泰豐'),
        ('師大鹽酥雞', '小吃', 25.023, 121.528, 4.0, 1, 'https://maps.google.com/?q=師大鹽酥雞'),
        
        # 台中地區餐廳
        ('屋馬燒肉 (園邸店)', '燒肉', 24.150, 120.665, 4.8, 3, 'https://maps.google.com/?q=屋馬燒肉園邸店'),
        ('輕井澤鍋物 (公益店)', '火鍋', 24.150, 120.651, 4.5, 2, 'https://maps.google.com/?q=輕井澤公益店'),
        ('宮原眼科', '甜點', 24.137, 120.683, 4.4, 2, 'https://maps.google.com/?q=宮原眼科'),
        ('第二市場 菜頭粿王', '小吃', 24.142, 120.678, 4.2, 1, 'https://maps.google.com/?q=第二市場菜頭粿王'),
        ('茶六燒肉堂 (朝富店)', '燒肉', 24.161, 120.638, 4.7, 3, 'https://maps.google.com/?q=茶六燒肉堂朝富店'),
        ('赤鬼牛排 (台灣大道店)', '西式', 24.152, 120.651, 4.1, 2, 'https://maps.google.com/?q=赤鬼牛排'),
        ('一中街 豐仁冰', '甜點', 24.151, 120.685, 4.3, 1, 'https://maps.google.com/?q=一中街豐仁冰'),
        ('逢甲夜市 明倫蛋餅', '小吃', 24.178, 120.645, 4.5, 1, 'https://maps.google.com/?q=明倫蛋餅'),
        ('第四信用合作社', '甜點', 24.138, 120.681, 4.3, 2, 'https://maps.google.com/?q=第四信用合作社'),
        ('春水堂 (四維創始店)', '茶館', 24.141, 120.665, 4.4, 2, 'https://maps.google.com/?q=春水堂四維創始店'),
        
        # 台中逢甲商圈餐廳
        ('激旨燒鳥 (逢甲總店)', '串燒', 24.180, 120.645, 4.6, 2, 'https://maps.google.com/?q=激旨燒鳥逢甲'),
        ('刁民酸菜魚 (逢甲店)', '中式', 24.176, 120.646, 4.7, 2, 'https://maps.google.com/?q=刁民酸菜魚逢甲'),
        ('日船章魚小丸子 (總店)', '小吃', 24.177, 120.645, 4.2, 1, 'https://maps.google.com/?q=日船章魚小丸子逢甲'),
        ('逢甲冰火菠蘿油', '甜點', 24.177, 120.644, 4.3, 1, 'https://maps.google.com/?q=逢甲冰火菠蘿油'),
        ('大甲芋頭城 (逢甲店)', '甜點', 24.178, 120.645, 4.4, 1, 'https://maps.google.com/?q=大甲芋頭城逢甲'),
        ('尊品原汁牛肉麵', '麵食', 24.175, 120.646, 4.1, 1, 'https://maps.google.com/?q=尊品原汁牛肉麵逢甲'),
        ('赤鬼炙燒牛排 (逢甲店)', '西式', 24.176, 120.644, 4.2, 2, 'https://maps.google.com/?q=赤鬼牛排逢甲'),
        ('炳叔烤玉米 (逢甲店)', '小吃', 24.177, 120.645, 4.5, 1, 'https://maps.google.com/?q=炳叔烤玉米逢甲'),
        ('官芝霖大腸包小腸', '小吃', 24.178, 120.646, 4.0, 1, 'https://maps.google.com/?q=官芝霖大腸包小腸'),
        ('一心素食臭豆腐', '素食', 24.179, 120.646, 4.4, 1, 'https://maps.google.com/?q=一心素食臭豆腐')
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
