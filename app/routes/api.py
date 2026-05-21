from flask import Blueprint, request, jsonify, session
from app.models.restaurant import recommend_restaurant, add_custom_restaurant
from app.models.history import add_history, get_history, update_history_feedback, delete_history
from app.models.favorite import add_favorite, remove_favorite, is_favorite, get_favorites
from app.models.database import get_db_connection
import uuid

api_bp = Blueprint('api', __name__, url_prefix='/api')

def init_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@api_bp.route('/recommend', methods=['POST'])
def recommend():
    init_session()
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
        
    try:
        min_rating = float(data.get('min_rating', 0.0))
    except ValueError:
        min_rating = 0.0
        
    categories_exclude = data.get('categories_exclude', [])
    only_favorites = bool(data.get('only_favorites', False))
    
    try:
        lat_float = float(lat) if lat else None
        lng_float = float(lng) if lng else None
    except ValueError:
        lat_float = None
        lng_float = None
        
    result = recommend_restaurant(
        lat_float, lng_float, 
        max_distance_km=distance, 
        budget_level=budget,
        categories_exclude=categories_exclude,
        min_rating=min_rating,
        only_favorites=only_favorites,
        session_id=session['session_id']
    )
    
    if result:
        # 紀錄歷史，此處包含真實的 restaurant_id 關聯
        add_history(session['session_id'], result['id'], result['name'], result['lat'], result['lng'])
        
        # 檢查該推薦結果是否已被此用戶收藏
        result['is_favorite'] = is_favorite(session['session_id'], result['id'])
        
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'message': '附近沒有符合篩選條件的餐廳喔！請調整防雷條件或換個位置再試試！'
        }), 404

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    init_session()
    conn = get_db_connection()
    try:
        rows = conn.execute(
            'SELECT DISTINCT category FROM restaurants WHERE is_custom = 0 OR session_id = ?',
            (session['session_id'],)
        ).fetchall()
        categories = [row['category'] for row in rows]
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        conn.close()

@api_bp.route('/favorites', methods=['GET'])
def list_favorites():
    init_session()
    try:
        favs = get_favorites(session['session_id'])
        return jsonify({
            'success': True,
            'data': favs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/favorites/toggle', methods=['POST'])
def toggle_favorite():
    init_session()
    data = request.get_json() or {}
    restaurant_id = data.get('restaurant_id')
    if not restaurant_id:
        return jsonify({'success': False, 'message': '缺少餐廳 ID'}), 400
        
    try:
        currently_fav = is_favorite(session['session_id'], restaurant_id)
        if currently_fav:
            remove_favorite(session['session_id'], restaurant_id)
            new_status = False
        else:
            add_favorite(session['session_id'], restaurant_id)
            new_status = True
            
        return jsonify({
            'success': True,
            'is_favorite': new_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/restaurants/custom', methods=['POST'])
def create_custom_restaurant():
    init_session()
    data = request.get_json() or {}
    name = data.get('name')
    category = data.get('category')
    google_maps_url = data.get('google_maps_url', '')
    
    if not name or not category:
        return jsonify({'success': False, 'message': '名稱與分類為必填欄位！'}), 400
        
    try:
        budget_level = int(data.get('budget_level', 1))
    except ValueError:
        budget_level = 1
        
    # 定位若為空，預設為台北市中心
    try:
        lat = float(data.get('lat', 25.041))
        lng = float(data.get('lng', 121.536))
    except (ValueError, TypeError):
        lat = 25.041
        lng = 121.536
        
    try:
        # 新增自訂餐廳
        new_id = add_custom_restaurant(
            session_id=session['session_id'],
            name=name,
            category=category,
            lat=lat,
            lng=lng,
            rating=5.0, # 自訂餐廳預設給 5.0 優良評價
            budget_level=budget_level,
            google_maps_url=google_maps_url or f"https://maps.google.com/?q={name}"
        )
        
        if new_id:
            # 新增成功後，自動將其加入我的收藏 (口袋名單)
            add_favorite(session['session_id'], new_id)
            return jsonify({
                'success': True,
                'message': '成功新增自訂私房餐廳，並已自動加入收藏！',
                'data': {'id': new_id, 'name': name, 'category': category}
            })
        else:
            return jsonify({'success': False, 'message': '新增失敗，請檢查輸入內容！'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/history', methods=['GET'])
def list_history():
    init_session()
    try:
        hist = get_history(session['session_id'])
        return jsonify({
            'success': True,
            'data': hist
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/history/<int:history_id>/feedback', methods=['POST'])
def save_feedback(history_id):
    init_session()
    data = request.get_json() or {}
    
    try:
        user_rating = int(data.get('user_rating'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '評分必須為 1-5 的整數！'}), 400
        
    comment = data.get('comment', '')
    
    try:
        success = update_history_feedback(session['session_id'], history_id, user_rating, comment)
        if success:
            return jsonify({'success': True, 'message': '感謝您的真實心得回饋！'})
        else:
            return jsonify({'success': False, 'message': '評估失敗，請確認該歷史紀錄屬於您。'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/history/<int:history_id>', methods=['DELETE'])
def delete_history_entry(history_id):
    init_session()
    try:
        success = delete_history(session['session_id'], history_id)
        if success:
            return jsonify({'success': True, 'message': '已刪除該條推薦歷史！'})
        else:
            return jsonify({'success': False, 'message': '刪除失敗，請確認該歷史紀錄屬於您。'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

