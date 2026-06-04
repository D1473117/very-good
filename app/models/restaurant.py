import math
import random
from app.models import db

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0.0)
    address = db.Column(db.String(255), nullable=False)
    price_level = db.Column(db.Integer, nullable=False)  # 1: 平價, 2: 中等, 3: 昂貴, 4: 奢華
    distance = db.Column(db.Integer, nullable=False, default=1000)    # in meters
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    is_custom = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.String(100), nullable=True)
    google_maps_url = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'rating': self.rating,
            'address': self.address,
            'price_level': self.price_level,
            'distance': self.distance,
            'lat': self.lat,
            'lng': self.lng,
            'is_custom': self.is_custom,
            'session_id': self.session_id,
            'google_maps_url': self.google_maps_url
        }

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

def recommend_restaurant(user_lat, user_lng, max_distance_km=3, price_levels=None, cuisines=None, min_rating=0.0, only_favorites=False, user_id=None, session_id=None):
    """
    整合 D1443860 推薦篩選演算法至 SQLAlchemy 模型查詢中。
    """
    query = Restaurant.query
    
    # 僅限口袋名單過濾
    if only_favorites and user_id:
        from app.models.favorite import Favorite
        query = query.join(Favorite).filter(Favorite.user_id == user_id)
        
    # 自訂私房菜與系統預設餐廳融合過濾
    if session_id:
        query = query.filter((Restaurant.is_custom == False) | (Restaurant.session_id == session_id))
    else:
        query = query.filter(Restaurant.is_custom == False)
        
    # 預算過濾
    if price_levels:
        price_levels = [int(p) for p in price_levels]
        query = query.filter(Restaurant.price_level.in_(price_levels))
        
    # 種類過濾
    if cuisines:
        query = query.filter(Restaurant.category.in_(cuisines))
        
    # 最低星等評分過濾
    if min_rating:
        query = query.filter(Restaurant.rating >= min_rating)
        
    restaurants = query.all()
    if not restaurants:
        return None
        
    # 經緯度距離計算與篩選
    filtered = []
    ref_lat = float(user_lat) if user_lat is not None else 25.041
    ref_lng = float(user_lng) if user_lng is not None else 121.536
    
    for r in restaurants:
        if r.lat is None or r.lng is None:
            # 若無經緯度，依據資料庫中預設 distance (公尺) 來判定
            if r.distance <= max_distance_km * 1000:
                filtered.append(r)
        else:
            dist = calculate_distance(ref_lat, ref_lng, r.lat, r.lng)
            if dist <= max_distance_km:
                filtered.append(r)
                
    # Fallback 機制 (若距離篩選無結果，退回沒有距離限制的結果)
    if not filtered:
        filtered = restaurants
        
    if not filtered:
        return None
        
    return random.choice(filtered)
