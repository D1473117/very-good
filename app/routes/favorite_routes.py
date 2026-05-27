from flask import Blueprint, request, redirect, url_for, render_template, flash
from app.models.favorite import Favorite

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/favorites', methods=['GET'])
def list_favorites():
    """顯示所有收藏餐廳的列表頁面"""
    favorites = Favorite.get_all()
    return render_template('favorites.html', favorites=favorites)

@favorite_bp.route('/favorites/add', methods=['POST'])
def add_favorite():
    """新增一筆收藏紀錄"""
    restaurant_name = request.form.get('restaurant_name')
    category = request.form.get('category')
    rating = request.form.get('rating')
    address = request.form.get('address')

    if not restaurant_name:
        flash('餐廳名稱為必填欄位', 'error')
        return redirect(request.referrer or url_for('favorite.list_favorites'))

    if rating:
        try:
            rating = int(rating)
        except ValueError:
            rating = None

    data = {
        'restaurant_name': restaurant_name,
        'category': category,
        'rating': rating,
        'address': address
    }
    
    favorite = Favorite.create(**data)
    if favorite:
        flash('成功加入收藏！', 'success')
    else:
        flash('加入收藏失敗，請稍後再試', 'error')

    return redirect(request.referrer or url_for('favorite.list_favorites'))

@favorite_bp.route('/favorites/delete/<int:id>', methods=['POST'])
def delete_favorite(id):
    """刪除指定的收藏紀錄"""
    success = Favorite.delete(id)
    if success:
        flash('收藏已刪除', 'success')
    else:
        flash('刪除失敗，找不到該紀錄', 'error')
        
    return redirect(url_for('favorite.list_favorites'))
