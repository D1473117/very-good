from flask import Blueprint, render_template, jsonify, session, request
from app.models import get_random_restaurant, get_restaurant_reviews

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/')
def index():
    """
    渲染首頁入口點，提供隨機推薦主要歡迎畫面。
    """
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering homepage: {e}")
        return "首頁載入失敗，請稍後再試！", 500

@recommendation_bp.route('/api/random')
def api_random_restaurant():
    """
    獲取隨機篩選餐廳及其評論資料。
    
    GET: 接收 Query 參數 (category, price_level, min_rating)，呼叫 get_random_restaurant() 執行條件隨機推薦 SQL。
    若成功選定餐廳，同時獲取其歷史評價並回傳 JSON；否則回傳 404 錯誤 JSON。
    """
    category = request.args.get('category', 'all')
    price_level = request.args.get('price_level', 'all')
    min_rating = request.args.get('min_rating', 'all')
    
    user_id = session.get('user_id')
    
    try:
        restaurant = get_random_restaurant(category, price_level, min_rating, user_id)
        
        if restaurant:
            # Fetch reviews for the recommended restaurant
            reviews = get_restaurant_reviews(restaurant['id'])
            return jsonify({
                "status": "success", 
                "data": restaurant,
                "reviews": reviews
            })
            
        return jsonify({
            "status": "error", 
            "message": "找不到符合篩選條件的餐廳，請調整篩選條件再試一次！"
        }), 404
    except Exception as e:
        print(f"Error in api_random_restaurant: {e}")
        return jsonify({
            "status": "error",
            "message": "系統推薦引擎發生異常，請稍後重試！"
        }), 500

