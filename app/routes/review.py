from flask import Blueprint

review_bp = Blueprint('review', __name__)

@review_bp.route('/reviews')
def reviews():
    """
    渲染我的評價歷史紀錄時間軸頁面。
    
    GET: 驗證登入狀態，呼叫 get_user_reviews() 查詢當前用戶發表過的所有評論歷史，渲染 reviews.html。
    """
    pass

@review_bp.route('/api/reviews/add', methods=['POST'])
def api_add_review():
    """
    新增對特定餐廳的饕客評價。
    
    POST: 接收 JSON 參數 (restaurant_id, rating, comment)，驗證後呼叫 add_review() 寫入資料庫，並返回該餐廳的最新評價清單。
    """
    pass

@review_bp.route('/api/reviews/delete/<int:review_id>', methods=['POST', 'DELETE'])
def api_delete_review(review_id):
    """
    刪除指定的餐廳評價紀錄。
    
    POST/DELETE: 接收路由參數 review_id，驗證評論是否屬當前登入用戶，呼叫 delete_review() 執行刪除並回傳 JSON 結果。
    """
    pass
