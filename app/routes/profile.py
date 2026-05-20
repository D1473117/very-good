from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/favorites')
@login_required
def favorites():
    """
    顯示當前使用者的收藏餐廳清單。
    
    調用 Favorite.get_by_user(current_user.id) 取得收藏清單。
    渲染 templates/profile/favorites.html。
    """
    pass

@profile_bp.route('/favorite/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    """
    切換餐廳收藏狀態 (AJAX 非同步端點)。
    
    接收 JSON 或表單中的 restaurant_id。
    1. 驗證該餐廳是否存在。
    2. 檢查 favorites 表是否已有該 (user_id, restaurant_id) 紀錄。
    3. 若有則刪除 (取消收藏)；若無則新增 (加入收藏)。
    
    回傳 JSON:
        - 新增成功: { "status": "success", "favorited": True }
        - 刪除成功: { "status": "success", "favorited": False }
    """
    pass

@profile_bp.route('/profile/history')
@login_required
def history():
    """
    顯示當前使用者的推薦歷史紀錄。
    
    接收 URL 查詢參數 page (預設 1) 及 limit (預設 10)。
    分頁查詢 RecommendationHistory.get_by_user(current_user.id, limit, offset)。
    
    渲染 templates/profile/history.html。
    """
    pass

@profile_bp.route('/profile/history/clear', methods=['POST'])
@login_required
def clear_history():
    """
    清空當前使用者的推薦歷史紀錄。
    
    調用 RecommendationHistory.clear_user_history(current_user.id) 清空紀錄。
    重導向至 /profile/history，並 Flash 提示歷史已清空。
    """
    pass
