"""
app/routes/favorite_routes.py

收藏功能路由 — F-05 收藏與歷史紀錄

Blueprint : favorite_bp
路由：
    GET  /favorites              list_favorites()   顯示收藏清單
    POST /favorites/add          add_favorite()     新增收藏
    POST /favorites/delete/<id>  delete_favorite()  刪除收藏
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.favorite import Favorite

favorite_bp = Blueprint('favorite', __name__)


# ------------------------------------------------------------------
# GET /favorites — 顯示收藏清單
# ------------------------------------------------------------------
@favorite_bp.route('/favorites', methods=['GET'])
@login_required
def list_favorites():
    """顯示目前所有收藏餐廳

    處理邏輯：
        1. 呼叫 Favorite.get_all() 取得清單（依 created_at 降序）
        2. 渲染 profile/favorites.html 並傳入清單

    輸出：
        render_template('profile/favorites.html', favorites=favorites)
    """
    favorites = Favorite.get_all()
    return render_template('profile/favorites.html', favorites=favorites)


# ------------------------------------------------------------------
# POST /favorites/add — 新增收藏
# ------------------------------------------------------------------
@favorite_bp.route('/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    """從表單接收餐廳資訊並新增收藏

    表單欄位：
        restaurant_name  必填  餐廳名稱
        category         選填  餐點類型
        rating           選填  評分（float）
        address          選填  餐廳地址

    處理邏輯：
        1. 取得並清理表單欄位
        2. 驗證 restaurant_name 不為空
        3. 呼叫 Favorite.create(...)
        4. 依結果顯示 flash 並重導向

    輸出（成功）：flash success → redirect /favorites
    輸出（失敗）：flash warning/danger → redirect /favorites
    """
    # 取得表單欄位
    restaurant_name = request.form.get('restaurant_name', '').strip()
    category        = request.form.get('category', '').strip() or None
    address         = request.form.get('address', '').strip() or None

    # rating 需轉型為 float；格式錯誤時設為 None
    try:
        rating = float(request.form.get('rating', ''))
    except (TypeError, ValueError):
        rating = None

    # --- 輸入驗證 ---
    if not restaurant_name:
        flash('新增失敗：餐廳名稱為必填欄位。', 'warning')
        return redirect(request.referrer or url_for('favorite.list_favorites'))

    # --- 寫入資料庫 ---
    result = Favorite.create(
        restaurant_name=restaurant_name,
        category=category,
        rating=rating,
        address=address,
    )

    if result:
        flash(f'「{restaurant_name}」已成功加入收藏！', 'success')
    else:
        flash('加入收藏時發生錯誤，請稍後再試。', 'danger')

    return redirect(url_for('favorite.list_favorites'))


# ------------------------------------------------------------------
# POST /favorites/delete/<id> — 刪除收藏
# ------------------------------------------------------------------
@favorite_bp.route('/favorites/delete/<int:favorite_id>', methods=['POST'])
@login_required
def delete_favorite(favorite_id):
    """依主鍵 ID 刪除指定收藏紀錄

    URL 參數：
        favorite_id  整數  收藏紀錄主鍵（Flask 自動轉型，非整數回傳 404）

    處理邏輯：
        1. 呼叫 Favorite.delete(favorite_id)
        2. 依結果顯示 flash 並重導向至收藏清單

    輸出（成功）：flash success → redirect /favorites
    輸出（找不到）：flash warning → redirect /favorites
    """
    success = Favorite.delete(favorite_id)

    if success:
        flash('已從收藏清單中移除。', 'success')
    else:
        flash('找不到此收藏紀錄，可能已被移除。', 'warning')

    return redirect(url_for('favorite.list_favorites'))
