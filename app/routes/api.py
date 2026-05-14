from flask import Blueprint, request, jsonify, session
from app.models.restaurant import recommend_restaurant
from app.models.history import add_history
import uuid

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    lat = data.get('lat')
    lng = data.get('lng')
    try:
        budget = int(data.get('budget', 3))
    except ValueError:
        budget = 3
        
    try:
        distance = float(data.get('distance', 5))
    except ValueError:
        distance = 5
    
    # 簡單的 session 處理，如果沒有設定 SECRET_KEY 或 session 會報錯
    # 我們在 app.py 已經有設定 SECRET_KEY
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        
    try:
        lat_float = float(lat) if lat else None
        lng_float = float(lng) if lng else None
    except ValueError:
        lat_float = None
        lng_float = None
        
    result = recommend_restaurant(lat_float, lng_float, max_distance_km=distance, budget_level=budget)
    
    if result:
        # 紀錄歷史
        add_history(session['session_id'], result['name'], result['lat'], result['lng'])
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'message': '附近沒有符合條件的餐廳喔！換個地點或條件試試看吧！'
        }), 404
