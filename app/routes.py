from flask import Blueprint, render_template, jsonify
from app.models import get_random_restaurant, init_db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    init_db() # Ensure DB is initialized
    return render_template('index.html')

@main_bp.route('/api/random')
def api_random_restaurant():
    restaurant = get_random_restaurant()
    if restaurant:
        return jsonify({"status": "success", "data": restaurant})
    return jsonify({"status": "error", "message": "No restaurants found"}), 404
