from flask import Blueprint

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/api/random')
def api_random_restaurant():
    """
    獲取隨機篩選餐廳及其評論資料。
    
    GET: 接收 Query 參數 (category, price_level, min_rating)，呼叫 get_random_restaurant() 執行條件隨機推薦 SQL。
    若成功選定餐廳，同時獲取其歷史評價並回傳 JSON；否則回傳 404 錯誤 JSON。
    """
    pass
