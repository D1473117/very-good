import random
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.models import db
from app.models.restaurant import Restaurant
from app.models.history import SpinHistory
from app.models.favorite import Favorite

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Dynamic fetch of all unique categories in restaurants to feed checkboxes!
    categories_query = db.session.query(Restaurant.category).distinct().all()
    categories = [cat[0] for cat in categories_query if cat[0]]
    
    return render_template('index.html', categories=categories)

@main_bp.route('/spin', methods=['POST'])
def spin():
    data = request.json or {}
    try:
        distance = int(data.get('distance', 3000))
    except ValueError:
        distance = 3000
        
    price_levels = data.get('price_level', [1, 2, 3, 4])
    cuisines = data.get('cuisines', [])
    
    # Query restaurants
    query = Restaurant.query.filter(Restaurant.distance <= distance)
    
    if price_levels:
        # Cast to integers just in case
        price_levels = [int(p) for p in price_levels]
        query = query.filter(Restaurant.price_level.in_(price_levels))
        
    if cuisines:
        query = query.filter(Restaurant.category.in_(cuisines))
        
    restaurants = query.all()
    
    if not restaurants:
        return jsonify({'error': '找不到符合條件的餐廳，請放寬篩選條件！'}), 404
        
    selected = random.choice(restaurants)
    
    # Check if favorited by current logged in user
    favorited = False
    if current_user.is_authenticated:
        fav_exists = Favorite.query.filter_by(
            user_id=current_user.id,
            restaurant_id=selected.id
        ).first()
        favorited = (fav_exists is not None)
        
        # Log to spin history
        history_entry = SpinHistory(
            user_id=current_user.id,
            restaurant_id=selected.id,
            distance=distance
        )
        db.session.add(history_entry)
        db.session.commit()
        
    response_data = selected.to_dict()
    response_data['favorited'] = favorited
    
    return jsonify(response_data)

@main_bp.route('/nearby')
def nearby():
    # Lists restaurants with custom filtering for exploring
    search_query = request.args.get('search', '')
    distance = request.args.get('distance', type=int)
    category = request.args.get('category', '')
    min_rating = request.args.get('rating', type=float)
    
    query = Restaurant.query
    
    if search_query:
        query = query.filter(
            Restaurant.name.ilike(f"%{search_query}%") | 
            Restaurant.address.ilike(f"%{search_query}%")
        )
    if distance:
        query = query.filter(Restaurant.distance <= distance)
    if category:
        query = query.filter(Restaurant.category == category)
    if min_rating:
        query = query.filter(Restaurant.rating >= min_rating)
        
    restaurants = query.all()
    
    # Dynamic categories list for filters
    categories_query = db.session.query(Restaurant.category).distinct().all()
    categories = [cat[0] for cat in categories_query if cat[0]]
    
    # Check favorites for UI heart status
    fav_ids = set()
    if current_user.is_authenticated:
        user_favs = Favorite.query.filter_by(user_id=current_user.id).all()
        fav_ids = {fav.restaurant_id for fav in user_favs}
        
    return render_template(
        'main/nearby.html',
        restaurants=restaurants,
        categories=categories,
        search=search_query,
        distance=distance,
        category=category,
        rating=min_rating,
        fav_ids=fav_ids
    )
