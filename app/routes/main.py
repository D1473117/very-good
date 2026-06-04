import random
import uuid
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user
from app.models import db
from app.models.restaurant import Restaurant, recommend_restaurant, calculate_distance
from app.models.history import SpinHistory
from app.models.favorite import Favorite

main_bp = Blueprint('main', __name__)

def get_current_session_id():
    """
    獲取目前的使用者識別碼，已登入用戶使用 user_<id>，訪客則自動分配 session UUID。
    """
    if current_user.is_authenticated:
        return f"user_{current_user.id}"
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return f"session_{session['session_id']}"

@main_bp.route('/')
def index():
    """
    顯示系統首頁/抽選畫面。
    """
    session_id = get_current_session_id()
    # 動態抓取系統內建以及該用戶新增的私房分類
    categories_query = db.session.query(Restaurant.category).filter(
        (Restaurant.is_custom == False) | (Restaurant.session_id == session_id)
    ).distinct().all()
    categories = [cat[0] for cat in categories_query if cat[0]]
    
    return render_template('index.html', categories=categories)

@main_bp.route('/spin', methods=['POST'])
def spin():
    """
    執行隨機推薦餐廳抽選 (整合 D1443860 的動態 GPS 推薦演算法)
    """
    data = request.json or {}
    
    # 收集地理定位經緯度
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    try:
        lat_float = float(lat) if lat is not None else None
        lng_float = float(lng) if lng is not None else None
    except ValueError:
        lat_float = None
        lng_float = None

    try:
        distance_limit = int(data.get('distance', 3000))
    except ValueError:
        distance_limit = 3000
        
    price_levels = data.get('price_level', [1, 2, 3, 4])
    cuisines = data.get('cuisines', [])
    min_rating = float(data.get('min_rating', 0.0))
    only_favorites = bool(data.get('only_favorites', False))
    
    session_id = get_current_session_id()
    user_id = current_user.id if current_user.is_authenticated else None
    
    # 呼叫動態地理位置推薦演算法
    selected = recommend_restaurant(
        user_lat=lat_float,
        user_lng=lng_float,
        max_distance_km=distance_limit / 1000.0,
        price_levels=price_levels,
        cuisines=cuisines,
        min_rating=min_rating,
        only_favorites=only_favorites,
        user_id=user_id,
        session_id=session_id
    )
    
    if not selected:
        return jsonify({'error': '找不到符合篩選條件的餐廳，請放寬您的限制！'}), 404
        
    # 檢查是否已收藏
    favorited = False
    if current_user.is_authenticated:
        fav_exists = Favorite.query.filter_by(
            user_id=current_user.id,
            restaurant_id=selected.id
        ).first()
        favorited = (fav_exists is not None)
        
        # 寫入抽選歷史紀錄
        history_entry = SpinHistory(
            user_id=current_user.id,
            restaurant_id=selected.id,
            distance=distance_limit
        )
        db.session.add(history_entry)
        db.session.commit()
        
    response_data = selected.to_dict()
    response_data['favorited'] = favorited
    
    # 計算動態距離 (公尺) 回傳給前端
    if lat_float is not None and lng_float is not None and selected.lat is not None and selected.lng is not None:
        calculated_dist = int(calculate_distance(lat_float, lng_float, selected.lat, selected.lng) * 1000)
        response_data['distance'] = calculated_dist
        
    return jsonify(response_data)

@main_bp.route('/nearby')
def nearby():
    """
    根據使用者目前位置，動態計算所有餐廳的距離並進行篩選排序。
    """
    search_query = request.args.get('search', '')
    distance_limit = request.args.get('distance', type=int)
    category = request.args.get('category', '')
    min_rating = request.args.get('rating', type=float)
    price_list = request.args.getlist('price', type=int)
    
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    # 使用 Fallback 預設基準點：大安中心 (25.041, 121.536)
    ref_lat = lat if lat is not None else 25.041
    ref_lng = lng if lng is not None else 121.536
    
    session_id = get_current_session_id()
    
    # 篩選系統預設與該使用者的自訂私房菜
    query = Restaurant.query.filter(
        (Restaurant.is_custom == False) | (Restaurant.session_id == session_id)
    )
    
    if search_query:
        query = query.filter(
            Restaurant.name.ilike(f"%{search_query}%") | 
            Restaurant.address.ilike(f"%{search_query}%")
        )
    if category:
        query = query.filter(Restaurant.category == category)
    if min_rating:
        query = query.filter(Restaurant.rating >= min_rating)
    if price_list:
        query = query.filter(Restaurant.price_level.in_(price_list))
        
    all_candidates = query.all()
    
    # 動態計算與排序
    restaurants_with_distance = []
    for r in all_candidates:
        if r.lat is not None and r.lng is not None:
            # 使用 Haversine 動態計算
            dist_meters = int(calculate_distance(ref_lat, ref_lng, r.lat, r.lng) * 1000)
        else:
            dist_meters = r.distance
            
        # 距離篩選限制
        if distance_limit and dist_meters > distance_limit:
            continue
            
        r_dict = r.to_dict()
        r_dict['distance'] = dist_meters
        restaurants_with_distance.append(r_dict)
        
    # 按距離排序
    restaurants_with_distance.sort(key=lambda x: x['distance'])
    
    # 動態抓取分類列表
    categories_query = db.session.query(Restaurant.category).filter(
        (Restaurant.is_custom == False) | (Restaurant.session_id == session_id)
    ).distinct().all()
    categories = [cat[0] for cat in categories_query if cat[0]]
    
    # 檢查收藏狀態
    fav_ids = set()
    if current_user.is_authenticated:
        user_favs = Favorite.query.filter_by(user_id=current_user.id).all()
        fav_ids = {fav.restaurant_id for fav in user_favs}
        
    return render_template(
        'main/nearby.html',
        restaurants=restaurants_with_distance,
        categories=categories,
        search=search_query,
        distance=distance_limit,
        category=category,
        rating=min_rating,
        price_list=price_list,
        fav_ids=fav_ids
    )
