from flask import Blueprint, render_template, abort

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/restaurant/<int:id>')
def detail(id):
    """
    顯示餐廳詳細資訊頁面。
    
    接收餐廳 ID。
    1. 自資料庫查詢對應 ID 的 Restaurant。
    2. 若已登入，檢查當前使用者是否已收藏此餐廳。
    
    渲染 templates/restaurant_detail.html。
    若餐廳不存在則回傳 HTTP 404。
    """
    pass
