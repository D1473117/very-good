from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.models.favorite import Favorite
from app.models.history import SpinHistory
from app.models.review import Review
from app.models.restaurant import Restaurant

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/favorites')
@login_required
def favorites():
    # Fetch all favorites for the logged-in user
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    restaurants = [fav.restaurant for fav in user_favorites if fav.restaurant]
    return render_template('profile/favorites.html', restaurants=restaurants)

@profile_bp.route('/profile/history')
@login_required
def history():
    # Fetch spin history and review history
    spins = SpinHistory.query.filter_by(user_id=current_user.id).order_by(SpinHistory.created_at.desc()).all()
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile/history.html', spins=spins, reviews=reviews)

@profile_bp.route('/favorite/toggle', methods=['POST'])
def toggle_favorite():
    # Manually check authentication to return 401 for AJAX requests
    if not current_user.is_authenticated:
        return jsonify({'error': '請先登入後再進行此操作！'}), 401
        
    data = request.json or {}
    restaurant_id = data.get('restaurant_id')
    
    if not restaurant_id:
        return jsonify({'error': '未提供餐廳 ID'}), 400
        
    try:
        res_id = int(restaurant_id)
    except ValueError:
        return jsonify({'error': '無效的餐廳 ID'}), 400
        
    restaurant = Restaurant.query.get(res_id)
    if not restaurant:
        return jsonify({'error': '找不到指定的餐廳'}), 404
        
    fav = Favorite.query.filter_by(user_id=current_user.id, restaurant_id=res_id).first()
    
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'status': 'success', 'favorited': False})
    else:
        new_fav = Favorite(user_id=current_user.id, restaurant_id=res_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'status': 'success', 'favorited': True})
