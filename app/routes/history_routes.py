from flask import Blueprint, request, redirect, url_for, render_template, flash
from app.models.history import History

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
def list_history():
    """顯示所有推薦歷史紀錄的列表頁面"""
    history_records = History.get_all()
    return render_template('history.html', history_records=history_records)

@history_bp.route('/history/add', methods=['POST'])
def add_history():
    """新增一筆推薦歷史紀錄"""
    restaurant_name = request.form.get('restaurant_name')
    category = request.form.get('category')
    rating = request.form.get('rating')

    if not restaurant_name:
        flash('餐廳名稱為必填欄位', 'error')
        return redirect(request.referrer or url_for('history.list_history'))

    if rating:
        try:
            rating = int(rating)
        except ValueError:
            rating = None

    data = {
        'restaurant_name': restaurant_name,
        'category': category,
        'rating': rating
    }
    
    history = History.create(**data)
    if history:
        flash('成功新增歷史紀錄！', 'success')
    else:
        flash('新增歷史紀錄失敗，請稍後再試', 'error')

    return redirect(request.referrer or url_for('history.list_history'))
