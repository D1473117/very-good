from flask import Blueprint

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/favorites')
def favorites():
    """
    渲染我的最愛收藏清單頁面。
    
    GET: 檢查 Session 登入狀態（若未登入則引導登入），呼叫 get_user_favorites() 讀取用戶的收藏清單，渲染 favorites.html。
    """
    pass

@favorite_bp.route('/api/favorites/toggle', methods=['POST'])
def api_toggle_favorite():
    """
    新增或取消餐廳收藏。
    
    POST: 接收 JSON 格式之 restaurant_id，呼叫 toggle_favorite() 即時切換最愛狀態並回傳 JSON 結果。
    """
    pass

@favorite_bp.route('/api/favorites/draw')
def api_draw_favorite():
    """
    從最愛收藏中隨機抽取一家餐廳。
    
    GET: 呼叫 get_random_favorite() 從用戶的最愛清單中隨機抽取一家餐廳並回傳 JSON 詳細資訊，若最愛為空則回傳 404。
    """
    pass
