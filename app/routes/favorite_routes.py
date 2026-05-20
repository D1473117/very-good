from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.favorite import Favorite

# 建立 收藏功能 的 Blueprint
favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/favorites', methods=['GET'])
@login_required
def list_favorites():
    """顯示目前登入使用者的收藏清單頁面"""
    try:
        favorites = Favorite.get_by_user(current_user.id)
        return render_template('profile/favorites.html', favorites=favorites)
    except Exception as e:
        flash(f"載入收藏清單時發生錯誤: {e}", "danger")
        return render_template('profile/favorites.html', favorites=[])

@favorite_bp.route('/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    """新增餐廳至收藏"""
    restaurant_id = request.form.get('restaurant_id', type=int)
    if not restaurant_id:
        flash("無效的餐廳識別碼", "warning")
        return redirect(request.referrer or url_for('favorite.list_favorites'))

    try:
        fav = Favorite.create(user_id=current_user.id, restaurant_id=restaurant_id)
        if fav:
            flash("成功加入收藏！", "success")
        else:
            flash("加入收藏失敗，請稍後再試。", "danger")
    except Exception as e:
        flash(f"系統錯誤: {e}", "danger")

    return redirect(request.referrer or url_for('favorite.list_favorites'))

@favorite_bp.route('/favorites/delete', methods=['POST'])
@login_required
def delete_favorite():
    """從收藏中刪除餐廳"""
    restaurant_id = request.form.get('restaurant_id', type=int)
    if not restaurant_id:
        flash("無效的餐廳識別碼", "warning")
        return redirect(request.referrer or url_for('favorite.list_favorites'))

    try:
        success = Favorite.delete(user_id=current_user.id, restaurant_id=restaurant_id)
        if success:
            flash("已從收藏清單中移除。", "success")
        else:
            flash("移除收藏失敗，該餐廳可能尚未被收藏。", "warning")
    except Exception as e:
        flash(f"系統錯誤: {e}", "danger")

    return redirect(request.referrer or url_for('favorite.list_favorites'))
