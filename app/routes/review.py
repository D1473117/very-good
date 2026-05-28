from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash
from app.models import get_user_reviews, add_review, get_restaurant_reviews, delete_review

review_bp = Blueprint('review', __name__)

@review_bp.route('/reviews')
def reviews():
    """
    渲染我的評價歷史紀錄時間軸頁面。
    
    GET: 驗證登入狀態，呼叫 get_user_reviews() 查詢當前用戶發表過的所有評論歷史，渲染 reviews.html。
    """
    if 'user_id' not in session:
        flash('請先登入以查看您的評論紀錄！', 'warning')
        return redirect(url_for('auth.login'))
        
    try:
        user_revs = get_user_reviews(session['user_id'])
        return render_template('reviews.html', reviews=user_revs)
    except Exception as e:
        print(f"Error loading user reviews: {e}")
        flash('載入評價歷史時發生錯誤，請稍後再試！', 'danger')
        return redirect(url_for('recommendation.index'))

@review_bp.route('/api/reviews/add', methods=['POST'])
def api_add_review():
    """
    新增對特定餐廳的饕客評價。
    
    POST: 接收 JSON 參數 (restaurant_id, rating, comment)，驗證後呼叫 add_review() 寫入資料庫，並返回該餐廳的最新評價清單。
    """
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入再發表評論！"}), 401
        
    data = request.get_json() or {}
    restaurant_id = data.get('restaurant_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    
    if not restaurant_id or not rating:
        return jsonify({"status": "error", "message": "餐廳 ID 與評分不可為空！"}), 400
        
    try:
        rating_val = int(rating)
        if rating_val < 1 or rating_val > 5:
            raise ValueError()
    except ValueError:
        return jsonify({"status": "error", "message": "評分必須是 1 至 5 之間的整數！"}), 400
        
    try:
        add_review(session['user_id'], int(restaurant_id), rating_val, comment)
        
        # Return updated reviews list to let frontend refresh dynamically
        updated_reviews = get_restaurant_reviews(int(restaurant_id))
        return jsonify({
            "status": "success", 
            "message": "評論已成功發布！",
            "reviews": updated_reviews
        })
    except Exception as e:
        print(f"Error adding review: {e}")
        return jsonify({"status": "error", "message": "發表評論失敗，請稍後重試！"}), 500

@review_bp.route('/api/reviews/delete/<int:review_id>', methods=['POST', 'DELETE'])
def api_delete_review(review_id):
    """
    刪除指定的餐廳評價紀錄。
    
    POST/DELETE: 接收路由參數 review_id，驗證評論是否屬當前登入用戶，呼叫 delete_review() 執行刪除並回傳 JSON 結果。
    """
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入！"}), 401
        
    try:
        success = delete_review(review_id, session['user_id'])
        if success:
            return jsonify({"status": "success", "message": "評論已成功刪除！"})
        return jsonify({"status": "error", "message": "無法刪除此評論，可能無此權限或評論不存在。"}), 403
    except Exception as e:
        print(f"Error deleting review {review_id}: {e}")
        return jsonify({"status": "error", "message": "刪除評論時發生系統異常，請稍後重試！"}), 500

