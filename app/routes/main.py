from flask import Blueprint, render_template, request, redirect, url_for, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    顯示系統首頁/抽選畫面。
    
    渲染 templates/index.html，初始化預設條件篩選。
    """
    pass

@main_bp.route('/spin', methods=['POST'])
def spin():
    """
    執行隨機推薦餐廳抽選。
    
    接收篩選條件 (category, price_range, distance, latitude, longitude)。
    1. 根據條件過濾餐廳。
    2. 隨機選出一間符合條件的餐廳。
    3. 若使用者已登入，將推薦紀錄自動寫入 SQLite 的 recommendation_histories 表中。
    
    回傳：
        - 同步請求：重導向至 /restaurant/<restaurant_id>
        - AJAX 請求：回傳 JSON { "status": "success", "restaurant_id": id }
    """
    pass

@main_bp.route('/nearby')
def nearby():
    """
    根據使用者位置顯示附近餐廳列表。
    
    接收 URL 參數 (lat, lng, distance)。
    利用 Haversine 公式計算各餐廳距離，篩選小於指定距離的餐廳，並依距離排序。
    
    渲染 templates/nearby.html。
    """
    pass
