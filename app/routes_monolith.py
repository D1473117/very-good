from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash
from app.models import (
    get_random_restaurant, init_db, create_user, check_user_credentials,
    toggle_favorite, get_user_favorites, get_random_favorite,
    add_review, get_restaurant_reviews, get_user_reviews, delete_review
)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

# ----------------- Auth Routes -----------------
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not password:
            flash('請輸入帳號和密碼！', 'danger')
            return render_template('register.html')
            
        if len(password) < 6:
            flash('密碼長度需至少為 6 個字元！', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('兩次輸入的密碼不一致！', 'danger')
            return render_template('register.html')
            
        user_id = create_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash('註冊成功！已自動為您登入。', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('帳號已被註冊，請換一個名字！', 'danger')
            
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('請輸入帳號和密碼！', 'danger')
            return render_template('login.html')
            
        user = check_user_credentials(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'歡迎回來，{user["username"]}！', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('帳號或密碼錯誤，請再試一次！', 'danger')
            
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出。', 'success')
    return redirect(url_for('main.index'))

# ----------------- Filtering & Draw API -----------------
@main_bp.route('/api/random')
def api_random_restaurant():
    category = request.args.get('category', 'all')
    price_level = request.args.get('price_level', 'all')
    min_rating = request.args.get('min_rating', 'all')
    
    user_id = session.get('user_id')
    restaurant = get_random_restaurant(category, price_level, min_rating, user_id)
    
    if restaurant:
        # Also fetch restaurant reviews to display
        reviews = get_restaurant_reviews(restaurant['id'])
        return jsonify({
            "status": "success", 
            "data": restaurant,
            "reviews": reviews
        })
        
    return jsonify({
        "status": "error", 
        "message": "找不到符合篩選條件的餐廳，請調整篩選條件再試一次！"
    }), 404

# ----------------- Favorites Routes & APIs -----------------
@main_bp.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash('請先登入以查看您的收藏！', 'warning')
        return redirect(url_for('main.login'))
    
    favs = get_user_favorites(session['user_id'])
    return render_template('favorites.html', favorites=favs)

@main_bp.route('/api/favorites/toggle', methods=['POST'])
def api_toggle_favorite():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入再進行收藏！"}), 401
        
    data = request.get_json() or {}
    restaurant_id = data.get('restaurant_id')
    
    if not restaurant_id:
        return jsonify({"status": "error", "message": "無效的餐廳 ID"}), 400
        
    is_fav = toggle_favorite(session['user_id'], int(restaurant_id))
    return jsonify({
        "status": "success", 
        "is_favorited": is_fav,
        "message": "已加入最愛！" if is_fav else "已取消收藏！"
    })

@main_bp.route('/api/favorites/draw')
def api_draw_favorite():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入！"}), 401
        
    restaurant = get_random_favorite(session['user_id'])
    if restaurant:
        reviews = get_restaurant_reviews(restaurant['id'])
        return jsonify({
            "status": "success", 
            "data": restaurant,
            "reviews": reviews
        })
        
    return jsonify({
        "status": "error", 
        "message": "您的最愛清單是空的，快去首頁抽籤並收藏幾家吧！"
    }), 404

# ----------------- Reviews Routes & APIs -----------------
@main_bp.route('/reviews')
def reviews():
    if 'user_id' not in session:
        flash('請先登入以查看您的評論紀錄！', 'warning')
        return redirect(url_for('main.login'))
        
    user_revs = get_user_reviews(session['user_id'])
    return render_template('reviews.html', reviews=user_revs)

@main_bp.route('/api/reviews/add', methods=['POST'])
def api_add_review():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入再發表評論！"}), 401
        
    data = request.get_json() or {}
    restaurant_id = data.get('restaurant_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    
    if not restaurant_id or not rating:
        return jsonify({"status": "error", "message": "餐廳 ID 與評分不可為空！"}), 400
        
    try:
        rating_val = int(rating)
        if rating_val < 1 or rating_val > 5:
            raise ValueError()
    except ValueError:
        return jsonify({"status": "error", "message": "評分必須是 1 至 5 之間的整數！"}), 400
        
    add_review(session['user_id'], int(restaurant_id), rating_val, comment)
    
    # Return updated reviews list to let frontend refresh dynamically
    updated_reviews = get_restaurant_reviews(int(restaurant_id))
    return jsonify({
        "status": "success", 
        "message": "評論已成功發布！",
        "reviews": updated_reviews
    })

@main_bp.route('/api/reviews/delete/<int:review_id>', methods=['POST', 'DELETE'])
def api_delete_review(review_id):
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "請先登入！"}), 401
        
    success = delete_review(review_id, session['user_id'])
    if success:
        return jsonify({"status": "success", "message": "評論已成功刪除！"})
    return jsonify({"status": "error", "message": "無法刪除此評論，可能無此權限或評論不存在。"}), 403
