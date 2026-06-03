from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db
from app.models.restaurant import Restaurant
from app.models.review import Review
from app.models.favorite import Favorite

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/restaurant/<int:restaurant_id>')
def detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).all()
    
    favorited = False
    if current_user.is_authenticated:
        fav = Favorite.query.filter_by(user_id=current_user.id, restaurant_id=restaurant_id).first()
        favorited = (fav is not None)
        
    return render_template(
        'restaurant/detail.html',
        restaurant=restaurant,
        reviews=reviews,
        favorited=favorited
    )

@restaurant_bp.route('/restaurant/<int:restaurant_id>/review', methods=['POST'])
@login_required
def submit_review(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Check if user already submitted a review
    existing_review = Review.query.filter_by(user_id=current_user.id, restaurant_id=restaurant_id).first()
    if existing_review:
        flash('您已經對這家餐廳發表過評論了！', 'warning')
        return redirect(url_for('restaurant.detail', restaurant_id=restaurant_id))
        
    rating_val = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    
    if not rating_val or not comment:
        flash('評分與評語皆為必填欄位！', 'error')
        return redirect(url_for('restaurant.detail', restaurant_id=restaurant_id))
        
    try:
        rating = float(rating_val)
        if not (1.0 <= rating <= 5.0):
            raise ValueError()
    except ValueError:
        flash('無效的評分數值！', 'error')
        return redirect(url_for('restaurant.detail', restaurant_id=restaurant_id))
        
    new_review = Review(
        user_id=current_user.id,
        restaurant_id=restaurant_id,
        rating=rating,
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()
    
    # Dynamic update of restaurant average rating
    all_reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
    total_rating = sum(r.rating for r in all_reviews)
    avg_rating = round(total_rating / len(all_reviews), 1)
    
    restaurant.rating = avg_rating
    db.session.commit()
    
    flash('評論發表成功！感謝您的分享 🌟', 'success')
    return redirect(url_for('restaurant.detail', restaurant_id=restaurant_id))
