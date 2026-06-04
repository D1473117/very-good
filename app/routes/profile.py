import uuid
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app.models import db
from app.models.favorite import Favorite
from app.models.history import SpinHistory
from app.models.review import Review
from app.models.restaurant import Restaurant

profile_bp = Blueprint('profile', __name__)

def get_current_session_id():
    """
    獲取目前的使用者識別碼，已登入用戶使用 user_<id>，訪客則自動分配 session UUID。
    """
    if current_user.is_authenticated:
        return f"user_{current_user.id}"
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return f"session_{session['session_id']}"

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

@profile_bp.route('/api/restaurants/custom', methods=['POST'])
def create_custom_restaurant():
    """
    新增使用者自訂私房餐廳 (整合 D1443860)。
    """
    data = request.json or {}
    name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    
    if not name or not category:
        return jsonify({'success': False, 'message': '餐廳名稱與分類皆為必填欄位！'}), 400
        
    try:
        price_level = int(data.get('price_level', 1))
    except ValueError:
        price_level = 1
        
    google_maps_url = data.get('google_maps_url', '').strip()
    if not google_maps_url:
        google_maps_url = f"https://maps.google.com/?q={name}"
        
    # 預設使用大安中心 fallback 座標
    lat = data.get('lat', 25.041)
    lng = data.get('lng', 121.536)
    
    session_id = get_current_session_id()
    
    try:
        new_restaurant = Restaurant(
            name=name,
            category=category,
            rating=5.0,
            address=data.get('address', '自訂私房菜位置'),
            price_level=price_level,
            distance=1000,
            lat=lat,
            lng=lng,
            is_custom=True,
            session_id=session_id,
            google_maps_url=google_maps_url
        )
        db.session.add(new_restaurant)
        db.session.commit()
        
        # 若使用者已登入，自動加入收藏口袋名單中
        if current_user.is_authenticated:
            new_fav = Favorite(user_id=current_user.id, restaurant_id=new_restaurant.id)
            db.session.add(new_fav)
            db.session.commit()
            
        return jsonify({
            'success': True,
            'message': f'成功新增私房餐廳「{name}」！',
            'data': new_restaurant.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
