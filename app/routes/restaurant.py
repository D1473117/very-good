from flask import Blueprint, render_template, abort
from app.models.restaurant import Restaurant
from app.models.favorite import Favorite

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/restaurant/<int:id>')
def detail(id):
    """
    顯示特定餐廳的詳細介紹頁面。
    
    1. 自資料庫查詢對應 ID 的 Restaurant。
    2. 檢查當前餐廳是否已被加入收藏。
    3. 渲染 templates/restaurant_detail.html。
    若餐廳不存在則回傳 HTTP 404。
    """
    restaurant = Restaurant.get_by_id(id)
    if not restaurant:
        abort(404)
        
    is_favorited = False
    try:
        # F-05 採用扁平式 favorites 表結構，故以餐廳名稱做為比對依據
        fav = Favorite.query.filter_by(restaurant_name=restaurant.name).first()
        is_favorited = fav is not None
    except Exception as e:
        print(f"Error checking favorite status in detail page: {str(e)}")
        
    return render_template('restaurant_detail.html', restaurant=restaurant, is_favorited=is_favorited)
