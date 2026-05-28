from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash
from app.models import get_user_favorites, toggle_favorite, get_random_favorite, get_restaurant_reviews

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/favorites')
def favorites():
    """
    渲染我的最愛收藏清單頁面。
    
    GET: 檢查 Session 登入狀態（若未登入則引導登入），呼叫 get_user_favorites() 讀取用戶的收藏清單，渲染 favorites.html。
    """
    if 'user_id' not in session:
        flash('請先登入以查看您的收藏！', 'warning')
        return redirect(url_for('auth.login'))
        
    try:
        favs = get_user_favorites(session['user_id'])
        return render_template('favorites.html', favorites=favs)
    except Exception as e:
        print(f"Error loading favorites: {e}")
        flash('載入收藏清單時發生錯誤，請稍後再試！', 'danger')
        return redirect(url_for('recommendation.index'))

@favorite_bp.route('/api/favorites/toggle', methods=['POST'])
def api_toggle_favorite():
    """
    新增或取消餐廳收藏。
    
    POST: 接收 JSON 格式之 restaurant_id，呼叫 toggle_favorite() 即時切換最愛狀態並回傳 JSON 結果。
    """
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入再進行收藏！"}), 401
        
    data = request.get_json() or {}
    restaurant_id = data.get('restaurant_id')
    
    if not restaurant_id:
        return jsonify({"status": "error", "message": "無效的餐廳 ID"}), 400
        
    try:
        is_fav = toggle_favorite(session['user_id'], int(restaurant_id))
        return jsonify({
            "status": "success", 
            "is_favorited": is_fav,
            "message": "已加入最愛！" if is_fav else "已取消收藏！"
        })
    except Exception as e:
        print(f"Error toggling favorite: {e}")
        return jsonify({"status": "error", "message": "操作收藏失敗，請稍後重試！"}), 500

@favorite_bp.route('/api/favorites/draw')
def api_draw_favorite():
    """
    從最愛收藏中隨機抽取一家餐廳。
    
    GET: 呼叫 get_random_favorite() 從用戶的最愛清單中隨機抽取一家餐廳並回傳 JSON 詳細資訊，若最愛為空則回傳 404。
    """
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入！"}), 401
        
    try:
        restaurant = get_random_favorite(session['user_id'])
        if restaurant:
            # Fetch reviews for the favorited restaurant
            reviews = get_restaurant_reviews(restaurant['id'])
            return jsonify({
                "status": "success", 
                "data": restaurant,
                "reviews": reviews
            })
            
        return jsonify({
            "status": "error", 
            "message": "您的最愛清單是空的，快去首頁抽籤並收藏幾家吧！"
        }), 404
    except Exception as e:
        print(f"Error drawing random favorite: {e}")
        return jsonify({"status": "error", "message": "抽取最愛發生異常，請重試！"}), 500

