from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.history import History

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
def list_history():
    """顯示所有推薦歷史紀錄"""
    try:
        histories = History.get_all()
        return render_template('history.html', histories=histories)
    except Exception as e:
        flash(f'載入歷史紀錄時發生錯誤: {str(e)}', 'error')
        return render_template('history.html', histories=[])

@history_bp.route('/history/add', methods=['POST'])
def add_history():
    """新增推薦歷史紀錄"""
    restaurant_name = request.form.get('restaurant_name')
    category = request.form.get('category')
    rating = request.form.get('rating')
    
    if not restaurant_name:
        flash('餐廳名稱為必填欄位', 'error')
        return redirect(url_for('history.list_history'))
        
    try:
        if rating:
            rating = float(rating)
            
        History.create(
            restaurant_name=restaurant_name,
            category=category,
            rating=rating
        )
        flash(f'成功新增歷史紀錄: {restaurant_name}', 'success')
    except Exception as e:
        flash(f'新增歷史紀錄失敗: {str(e)}', 'error')
        
    return redirect(url_for('history.list_history'))
