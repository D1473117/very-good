"""
app/routes/history_routes.py

歷史推薦紀錄路由 — F-05 收藏與歷史紀錄

Blueprint : history_bp
路由：
    GET  /history       list_history()  顯示歷史清單（含分頁）
    POST /history/add   add_history()   新增歷史紀錄（抽選後系統呼叫）
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.history import History

history_bp = Blueprint('history', __name__)

# 每頁顯示筆數
ITEMS_PER_PAGE = 10


# ------------------------------------------------------------------
# GET /history — 顯示歷史推薦紀錄（含分頁）
# ------------------------------------------------------------------
@history_bp.route('/history', methods=['GET'])
@login_required
def list_history():
    """顯示歷史推薦紀錄列表，支援分頁

    URL Query String：
        page  整數（選填，預設 1）

    處理邏輯：
        1. 從 URL 取得 page 參數
        2. 計算 offset = (page - 1) * ITEMS_PER_PAGE
        3. 呼叫 History.get_all(limit, offset) 取得當頁資料
        4. 查詢總筆數並計算 total_pages
        5. 渲染 profile/history.html

    輸出：
        render_template('profile/history.html',
                        histories=histories,
                        page=page,
                        total_pages=total_pages)
    """
    # 取得分頁參數（非整數自動回傳 400）
    page   = request.args.get('page', 1, type=int)
    page   = max(page, 1)          # 防止負數頁碼
    offset = (page - 1) * ITEMS_PER_PAGE

    # 取得當頁資料
    histories = History.get_all(limit=ITEMS_PER_PAGE, offset=offset)

    # 計算總頁數
    total_count = History.query.count()
    total_pages = max(1, (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

    # 防止頁碼超出範圍
    if page > total_pages and total_count > 0:
        return redirect(url_for('history.list_history', page=total_pages))

    return render_template(
        'profile/history.html',
        histories=histories,
        page=page,
        total_pages=total_pages,
    )


# ------------------------------------------------------------------
# POST /history/add — 新增歷史紀錄
# ------------------------------------------------------------------
@history_bp.route('/history/add', methods=['POST'])
@login_required
def add_history():
    """新增一筆推薦歷史紀錄

    由隨機抽選路由（/spin）在推薦完成後呼叫。
    也可在餐廳詳情頁面以隱藏表單呼叫。

    表單欄位：
        restaurant_name  必填  餐廳名稱
        category         選填  餐點類型
        rating           選填  評分（float）

    處理邏輯：
        1. 取得並清理表單欄位
        2. 驗證 restaurant_name 不為空
        3. 呼叫 History.create(...)
        4. 依結果顯示 flash 並重導向

    輸出（成功）：flash info → redirect 至 referrer 或 /history
    輸出（失敗）：flash warning/danger → redirect 至 referrer 或 /history
    """
    # 取得表單欄位
    restaurant_name = request.form.get('restaurant_name', '').strip()
    category        = request.form.get('category', '').strip() or None

    # rating 需轉型為 float；格式錯誤時設為 None
    try:
        rating = float(request.form.get('rating', ''))
    except (TypeError, ValueError):
        rating = None

    # 決定成功後重導向目標
    next_url = request.form.get('next') or request.referrer or url_for('history.list_history')

    # --- 輸入驗證 ---
    if not restaurant_name:
        flash('歷史紀錄寫入失敗：餐廳名稱不可為空。', 'warning')
        return redirect(next_url)

    # --- 寫入資料庫 ---
    result = History.create(
        restaurant_name=restaurant_name,
        category=category,
        rating=rating,
    )

    if result:
        flash(f'已記錄本次推薦：「{restaurant_name}」', 'info')
    else:
        flash('歷史紀錄寫入失敗，請稍後再試。', 'danger')

    return redirect(next_url)
