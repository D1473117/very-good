import math
import random
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app.models import db
from app.models.restaurant import Restaurant
from app.models.history import History

main_bp = Blueprint('main', __name__)

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    計算兩個經緯度之間的距離（公尺）。
    使用 Haversine 公式。
    """
    R = 6371.0  # 地球半徑 (公里)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_meters = R * c * 1000.0
    return distance_meters

@main_bp.route('/')
def index():
    """
    顯示系統首頁/抽選畫面。
    載入所有類別與價格區間以初始化篩選下拉選單。
    """
    try:
        # 動態抓取資料庫中現有的類別與價格範圍
        categories_query = db.session.query(Restaurant.category).distinct().all()
        categories = sorted([c[0] for c in categories_query if c[0]])
        
        price_ranges_query = db.session.query(Restaurant.price_range).distinct().all()
        price_ranges = sorted([p[0] for p in price_ranges_query if p[0]])
    except Exception as e:
        categories = ["中式", "日式", "韓式", "美式", "義式", "火鍋", "素食", "飲料", "甜點"]
        price_ranges = ["$50 以下", "$50-$150", "$150-$300", "$300+"]
        print(f"Error loading filters from DB: {str(e)}")

    return render_template('index.html', categories=categories, price_ranges=price_ranges)

@main_bp.route('/spin', methods=['POST'])
def spin():
    """
    執行隨機推薦餐廳抽選。
    接收篩選條件：category, price_range, distance, latitude, longitude。
    基於條件過濾餐廳，隨機挑選一間，並記錄至 history 資料庫。
    支持 Form 表單提交與 AJAX (JSON)。
    """
    # 支援 JSON 或是 Form 表單的傳入方式
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form or {}

    category = data.get('category', '').strip()
    price_range = data.get('price_range', '').strip()
    distance_str = data.get('distance', '').strip()
    
    # 經緯度定位資料
    lat_str = data.get('latitude', '').strip()
    lng_str = data.get('longitude', '').strip()

    try:
        query = Restaurant.query
        
        # 1. 類別篩選
        if category and category != '全部':
            query = query.filter(Restaurant.category == category)
            
        # 2. 價格篩選
        if price_range and price_range != '全部':
            query = query.filter(Restaurant.price_range == price_range)
            
        restaurants = query.all()
        
        # 3. 距離篩選
        user_lat = None
        user_lng = None
        if lat_str and lng_str:
            try:
                user_lat = float(lat_str)
                user_lng = float(lng_str)
            except ValueError:
                pass
                
        # 如果使用者指定了距離且經緯度有效
        if user_lat is not None and user_lng is not None and distance_str and distance_str != '不限':
            try:
                max_distance = float(distance_str) # 公尺
                filtered_by_dist = []
                for r in restaurants:
                    if r.latitude is not None and r.longitude is not None:
                        dist = haversine_distance(user_lat, user_lng, r.latitude, r.longitude)
                        if dist <= max_distance:
                            # 附加計算出來的距離，方便前端使用
                            r.temp_distance = round(dist)
                            filtered_by_dist.append(r)
                restaurants = filtered_by_dist
            except ValueError:
                pass

        # 若無符合篩選條件的餐廳
        if not restaurants:
            msg = "找不到符合篩選條件的餐廳，請放寬篩選範圍！"
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 404
            else:
                flash(msg, "error")
                return redirect(url_for('main.index'))

        # 4. 隨機選出一間
        chosen = random.choice(restaurants)

        # 5. 寫入推薦歷史紀錄 (F-05 扁平表格式)
        try:
            History.create(
                restaurant_name=chosen.name,
                category=chosen.category,
                rating=chosen.rating
            )
        except Exception as he:
            print(f"Error logging recommendation history: {str(he)}")

        # 6. 回傳結果
        if request.is_json:
            distance_val = getattr(chosen, 'temp_distance', None)
            # 若定位存在但沒有附帶 temp_distance（因為選了不限距離），則計算出來
            if distance_val is None and user_lat is not None and user_lng is not None and chosen.latitude is not None and chosen.longitude is not None:
                distance_val = round(haversine_distance(user_lat, user_lng, chosen.latitude, chosen.longitude))

            return jsonify({
                "status": "success",
                "restaurant": {
                    "id": chosen.id,
                    "name": chosen.name,
                    "category": chosen.category,
                    "price_range": chosen.price_range,
                    "rating": chosen.rating,
                    "address": chosen.address,
                    "phone": chosen.phone or "暫無提供",
                    "operating_hours": chosen.operating_hours or "暫無提供",
                    "image_url": chosen.image_url,
                    "google_maps_url": chosen.google_maps_url,
                    "distance": distance_val
                }
            })
        else:
            return redirect(url_for('restaurant.detail', id=chosen.id))
            
    except Exception as e:
        msg = f"抽選餐廳時發生異常: {str(e)}"
        if request.is_json:
            return jsonify({"status": "error", "message": msg}), 500
        else:
            flash(msg, "error")
            return redirect(url_for('main.index'))

@main_bp.route('/nearby')
def nearby():
    """
    根據使用者位置顯示附近餐廳列表。
    接收 URL 參數 (lat, lng, distance)。
    利用 Haversine 公式計算各餐廳距離，篩選小於指定距離的餐廳，並依距離排序。
    """
    lat_str = request.args.get('lat', '').strip()
    lng_str = request.args.get('lng', '').strip()
    dist_str = request.args.get('distance', '500').strip() # 預設 500m
    
    if not lat_str or not lng_str:
        flash("請提供定位座標以查詢附近餐廳！", "error")
        return redirect(url_for('main.index'))
        
    try:
        user_lat = float(lat_str)
        user_lng = float(lng_str)
        max_dist = float(dist_str)
        
        all_restaurants = Restaurant.get_all()
        nearby_list = []
        
        for r in all_restaurants:
            if r.latitude is not None and r.longitude is not None:
                dist = haversine_distance(user_lat, user_lng, r.latitude, r.longitude)
                if dist <= max_dist:
                    r.temp_distance = round(dist)
                    nearby_list.append(r)
                    
        # 依距離由近到遠排序
        nearby_list.sort(key=lambda x: x.temp_distance)
        
        return render_template('nearby.html', restaurants=nearby_list, user_lat=user_lat, user_lng=user_lng, search_distance=max_dist)
        
    except ValueError:
        flash("經緯度或距離格式錯誤！", "error")
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f"搜尋附近餐廳時發生錯誤: {str(e)}", "error")
        return redirect(url_for('main.index'))
