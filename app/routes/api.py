from flask import Blueprint, request, jsonify, session
from app.models.restaurant import recommend_restaurant, add_custom_restaurant, get_all_restaurants
from app.models.history import add_history, get_history, delete_history, update_history_feedback
from app.models.favorite import add_favorite, remove_favorite, is_favorite, get_favorites
from app.models.database import get_db_connection
import uuid

api_bp = Blueprint('api', __name__, url_prefix='/api')

def init_session():
    """
    初始化 Session，若無則生成唯一識別碼 UUID。
    """
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
        lat_float = float(lat) if lat is not None else None
        lng_float = float(lng) if lng is not None else None
    except ValueError:
        lat_float = None
        lng_float = None
        
    min_rating = float(data.get('min_rating', 0.0))
    categories_exclude = data.get('categories_exclude', [])
    only_favorites = bool(data.get('only_favorites', False))
    
    result = recommend_restaurant(
        lat_float, lng_float, 
        max_distance_km=distance, 
        budget_level=budget,
        session_id=session['session_id'],
        min_rating=min_rating,
        categories_exclude=categories_exclude,
        only_favorites=only_favorites
    )
    
    if result:
        # 紀錄推薦歷史
        add_history(session['session_id'], result['id'], result['name'], result['lat'], result['lng'])
        return jsonify({
            'success': True,
            'data': result
        })
    else:
        return jsonify({
            'success': False,
            'message': '附近沒有符合篩選條件的餐廳喔！請調整預算、距離範圍，或在避雷針關閉部分排除分類再試試！'
        }), 404

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    init_session()
    conn = get_db_connection()
    try:
        # 動態抓取系統內建以及該用戶新增的私房分類
        rows = conn.execute(
            '''SELECT DISTINCT category FROM restaurants 
               WHERE is_custom = 0 OR (is_custom = 1 AND session_id = ?)
               ORDER BY category ASC''',
            (session['session_id'],)
        ).fetchall()
        categories = [row['category'] for row in rows if row['category']]
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
        return jsonify({'success': False, 'message': '餐廳 ID 缺失！'}), 400
        
    try:
        restaurant_id = int(restaurant_id)
        fav_status = is_favorite(session['session_id'], restaurant_id)
        
        if fav_status:
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
    name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    
    if not name or not category:
        return jsonify({'success': False, 'message': '餐廳名稱與分類皆為必填欄位！'}), 400
        
    try:
        budget_level = int(data.get('budget_level', 1))
    except ValueError:
        budget_level = 1
        
    google_maps_url = data.get('google_maps_url', '').strip()
    if not google_maps_url:
        google_maps_url = f"https://maps.google.com/?q={name}"
        
    # 預設台北大安中心坐標，若能在 Session 中找到最新推薦或定位可替換，
    # 這裡採用計畫中的 Fallback 決策 (25.041, 121.536)
    lat = 25.041
    lng = 121.536
    
    try:
        new_id = add_custom_restaurant(
            session['session_id'], 
            name, category, 
            lat, lng, 
            rating=5.0, 
            budget_level=budget_level, 
            google_maps_url=google_maps_url
        )
        
        if new_id:
            # 決策優化：自動加入收藏口袋名單中
            add_favorite(session['session_id'], new_id)
            return jsonify({
                'success': True,
                'message': f'成功新增私房餐廳「{name}」，並已自動加入口袋名單！',
                'data': {
                    'id': new_id,
                    'name': name,
                    'category': category,
                    'budget_level': budget_level,
                    'google_maps_url': google_maps_url
                }
            })
        else:
            return jsonify({'success': False, 'message': '資料庫新增餐廳失敗！'}), 500
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
        user_rating = int(data.get('user_rating', 0))
    except ValueError:
        user_rating = 0
        
    comment = data.get('comment', '').strip()
    
    if user_rating < 1 or user_rating > 5:
        return jsonify({'success': False, 'message': '評分星等必須介於 1 至 5 顆星之間！'}), 400
        
    try:
        success = update_history_feedback(session['session_id'], history_id, user_rating, comment)
        if success:
            return jsonify({'success': True, 'message': '感謝您的美食心得真實回饋！'})
        else:
            return jsonify({'success': False, 'message': '更新失敗，請確認該歷史紀錄屬於您。'}), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

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
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
