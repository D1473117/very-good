from flask import Blueprint, render_template, request, redirect, url_for, jsonify

vote_bp = Blueprint('vote', __name__, url_prefix='/vote')

@vote_bp.route('/create', methods=['GET', 'POST'])
def create_room():
    """
    建立多人投票房間。
    
    GET: 渲染 templates/vote/create.html 建立房間設定頁面。
    POST: 接收條件設定，建立房間紀錄，生成 6 碼英數代碼，並重導向至房間頁面。
    """
    pass

@vote_bp.route('/room/<room_code>')
def room(room_code):
    """
    進入特定的投票房間頁面。
    
    接收房間代碼，驗證房間是否存在與有效性。
    渲染 templates/vote/room.html，供參與者投票並顯示計時與即時票數。
    """
    pass

@vote_bp.route('/room/<room_code>/vote', methods=['POST'])
def vote(room_code):
    """
    對投票房間內指定餐廳提交一票。
    
    接收餐廳 ID。累加該餐廳的得票數。
    回傳 JSON: { "status": "success", "message": "投票成功" }
    """
    pass

@vote_bp.route('/room/<room_code>/status')
def room_status(room_code):
    """
    獲取投票房間的目前狀態 (輪詢用 API)。
    
    回傳 JSON: { "votes": { restaurant_id: count }, "closed": true/false, "winner": restaurant_id }
    """
    pass
