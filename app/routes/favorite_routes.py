from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.favorite import Favorite

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/favorites', methods=['GET'])
def list_favorites():
    """顯示所有收藏餐廳"""
    try:
        favorites = Favorite.get_all()
        return render_template('favorites.html', favorites=favorites)
    except Exception as e:
        flash(f'載入收藏清單時發生錯誤: {str(e)}', 'error')
        return render_template('favorites.html', favorites=[])

@favorite_bp.route('/favorites/add', methods=['POST'])
def add_favorite():
    """新增收藏餐廳"""
    restaurant_name = request.form.get('restaurant_name')
    category = request.form.get('category')
    rating = request.form.get('rating')
    address = request.form.get('address')
    
    if not restaurant_name:
        flash('餐廳名稱為必填欄位', 'error')
        return redirect(url_for('favorite.list_favorites'))
        
    try:
        if rating:
            rating = float(rating)
            
        Favorite.create(
            restaurant_name=restaurant_name,
            category=category,
            rating=rating,
            address=address
        )
        flash(f'成功新增收藏: {restaurant_name}', 'success')
    except Exception as e:
        flash(f'新增收藏失敗: {str(e)}', 'error')
        
    return redirect(url_for('favorite.list_favorites'))

@favorite_bp.route('/favorites/delete/<int:id>', methods=['POST'])
def delete_favorite(id):
    """根據 ID 刪除收藏餐廳"""
    try:
        success = Favorite.delete(id)
        if success:
            flash('成功刪除收藏', 'success')
        else:
            flash('找不到指定的收藏紀錄', 'error')
    except Exception as e:
        flash(f'刪除收藏失敗: {str(e)}', 'error')
        
    return redirect(url_for('favorite.list_favorites'))
