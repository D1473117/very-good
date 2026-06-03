from flask import Blueprint, request, jsonify, render_template, url_for
from app.models.voting_room import VotingRoom
from app.models.room_candidate import RoomCandidate

# 建立 F-06 專屬的 Blueprint
voting_bp = Blueprint('voting', __name__)

@voting_bp.route('/voting/create', methods=['POST'])
def create_room():
    """建立投票房間並加入候選餐廳"""
    # 支援 JSON 與 Form 傳遞格式
    if request.is_json:
        data = request.get_json() or {}
        restaurant_ids = data.get('restaurant_ids', [])
    else:
        restaurant_ids = request.form.getlist('restaurant_ids')
    
    if not restaurant_ids or len(restaurant_ids) < 2:
        return jsonify({"status": "error", "message": "至少需要兩間餐廳才能發起投票喔！"}), 400
        
    # 呼叫 Model 建立房間
    room_id = VotingRoom.create_room()
    
    # 將候選餐廳逐一加入該房間
    try:
        for r_id in restaurant_ids:
            RoomCandidate.add_candidate(room_id, int(r_id))
    except Exception as e:
        # 若加入失敗則將房間刪除以維持一致性
        VotingRoom.delete(room_id)
        return jsonify({"status": "error", "message": f"加入候選餐廳時發生錯誤: {str(e)}"}), 500
        
    # 產生要讓大家複製分享的完整網址
    room_url = url_for('voting.room', room_id=room_id, _external=True)
    
    return jsonify({
        "status": "success", 
        "room_id": room_id, 
        "room_url": room_url
    })

@voting_bp.route('/voting/<room_id>', methods=['GET'])
def room(room_id):
    """進入特定投票房間的畫面"""
    room_obj = VotingRoom.get_by_id(room_id)
    if not room_obj:
        return "找不到該投票房間，或房間已失效", 404
        
    candidates = RoomCandidate.get_by_room_id(room_id)
    
    # 將 SQLAlchemy 物件序列化為字典，以完全相容前端可能使用的 dict key 存取 (如 candidate['name'])
    formatted_candidates = []
    for c in candidates:
        if c.restaurant:
            formatted_candidates.append({
                "id": c.restaurant.id,
                "name": c.restaurant.name,
                "category": c.restaurant.category,
                "vote_count": c.vote_count,
                "image_url": c.restaurant.image_url
            })
            
    return render_template('voting_room.html', room_id=room_id, candidates=formatted_candidates)

@voting_bp.route('/voting/<room_id>/vote', methods=['POST'])
def vote(room_id):
    """處理朋友點擊投票的動作"""
    if request.is_json:
        data = request.get_json() or {}
        restaurant_id = data.get('restaurant_id')
    else:
        restaurant_id = request.form.get('restaurant_id')
    
    if not restaurant_id:
        return jsonify({"status": "error", "message": "缺少餐廳 ID"}), 400
        
    # 呼叫 Model 增加票數
    result = RoomCandidate.vote(room_id, int(restaurant_id))
    if not result:
        return jsonify({"status": "error", "message": "投票失敗，該房間內找不到該候選餐廳"}), 404
        
    return jsonify({"status": "success", "message": "投票成功！"})

@voting_bp.route('/voting/<room_id>/results', methods=['GET'])
def results(room_id):
    """取得該房間最新的票數 (讓前端 JS 每秒自動更新畫面用)"""
    room_obj = VotingRoom.get_by_id(room_id)
    if not room_obj:
        return jsonify({"status": "error", "message": "找不到該投票房間"}), 404
        
    candidates = RoomCandidate.get_by_room_id(room_id)
    
    return jsonify({
        "status": "success",
        "results": [{"restaurant_id": c.restaurant_id, "vote_count": c.vote_count} for c in candidates]
    })

# 為了向後相容 app/routes/__init__.py 的匯出，提供 vote_bp 別名
vote_bp = voting_bp
