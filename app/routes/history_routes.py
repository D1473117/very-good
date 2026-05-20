from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.history import RecommendationHistory

# 建立 歷史紀錄功能 的 Blueprint
history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
@login_required
def list_history():
    """顯示目前登入使用者的歷史推薦紀錄列表，支援分頁"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = 10
        offset = (page - 1) * limit
        
        histories = RecommendationHistory.get_by_user(current_user.id, limit=limit, offset=offset)
        
        # 計算總頁數
        total_count = RecommendationHistory.query.filter_by(user_id=current_user.id).count()
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
        
        return render_template(
            'profile/history.html', 
            histories=histories, 
            page=page, 
            total_pages=total_pages
        )
    except Exception as e:
        flash(f"載入歷史紀錄時發生錯誤: {e}", "danger")
        return render_template('profile/history.html', histories=[], page=1, total_pages=1)

@history_bp.route('/history/add', methods=['POST'])
@login_required
def add_history():
    """新增推薦歷史紀錄"""
    restaurant_id = request.form.get('restaurant_id', type=int)
    if not restaurant_id:
        flash("無效的餐廳識別碼", "warning")
        return redirect(request.referrer or url_for('history.list_history'))

    try:
        history = RecommendationHistory.create(user_id=current_user.id, restaurant_id=restaurant_id)
        if history:
            flash("已成功記錄本次推薦餐食。", "info")
        else:
            flash("寫入歷史紀錄失敗。", "warning")
    except Exception as e:
        flash(f"系統錯誤: {e}", "danger")

    return redirect(request.referrer or url_for('history.list_history'))

@history_bp.route('/history/clear', methods=['POST'])
@login_required
def clear_history():
    """清空目前登入使用者的所有歷史推薦紀錄"""
    try:
        success = RecommendationHistory.clear_user_history(current_user.id)
        if success:
            flash("歷史推薦紀錄已成功清空。", "success")
        else:
            flash("清空歷史紀錄失敗，請稍後再試。", "danger")
    except Exception as e:
        flash(f"系統錯誤: {e}", "danger")

    return redirect(url_for('history.list_history'))
