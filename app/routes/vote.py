import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from app.models import db
from app.models.restaurant import Restaurant
from app.models.vote import VoteRoom, VoteOption

vote_bp = Blueprint('vote', __name__)

@vote_bp.route('/vote')
def lobby():
    # Show active voting rooms or a create room card
    rooms = VoteRoom.query.order_by(VoteRoom.created_at.desc()).limit(10).all()
    # 傳遞所有餐廳供前端 datalist 搜尋使用
    all_restaurants = Restaurant.query.with_entities(Restaurant.id, Restaurant.name).all()
    return render_template('vote/lobby.html', rooms=rooms, all_restaurants=all_restaurants)

@vote_bp.route('/vote/create', methods=['POST'])
def create_room():
    title = request.form.get('title', '').strip()
    if not title:
        title = "今天吃什麼？美味對決！"
        
    # Get manually selected restaurant IDs
    manual_ids = request.form.getlist('restaurant_ids')
    manual_ids = [int(i) for i in manual_ids if i.isdigit()]
    
    # Get random count
    random_count = request.form.get('random_count', type=int, default=0)
    if random_count < 0:
        random_count = 0
        
    if not manual_ids and random_count == 0:
        flash('請至少手動挑選一家餐廳，或是設定隨機抽取數量！', 'error')
        return redirect(url_for('vote.lobby'))

    candidates = []
    
    # 1. Add manual candidates
    if manual_ids:
        manual_candidates = Restaurant.query.filter(Restaurant.id.in_(manual_ids)).all()
        candidates.extend(manual_candidates)
        
    # 2. Add random candidates
    if random_count > 0:
        # Get all IDs excluding manual ones
        query = Restaurant.query.with_entities(Restaurant.id)
        if manual_ids:
            query = query.filter(~Restaurant.id.in_(manual_ids))
        available_ids = [r.id for r in query.all()]
        
        if available_ids:
            random_picks = random.sample(available_ids, min(random_count, len(available_ids)))
            random_candidates = Restaurant.query.filter(Restaurant.id.in_(random_picks)).all()
            candidates.extend(random_candidates)
            
    if len(candidates) < 2:
        flash('選項數量不足，無法建立投票！請至少加入或抽取 2 家餐廳。', 'error')
        return redirect(url_for('vote.lobby'))
        
    # Create room
    room = VoteRoom(title=title)
    db.session.add(room)
    db.session.commit() # Generate room ID
    
    # Create options
    for res in candidates:
        opt = VoteOption(room_id=room.id, restaurant_id=res.id)
        db.session.add(opt)
    db.session.commit()
    
    flash('投票房間已成功建立！快分享連結給朋友吧 🔗', 'success')
    return redirect(url_for('vote.room', room_id=room.id))

@vote_bp.route('/vote/<room_id>')
def room(room_id):
    room_obj = VoteRoom.query.get_or_404(room_id)
    
    # Calculate percentage votes for UI bars
    options = VoteOption.query.filter_by(room_id=room_id).all()
    total_votes = sum(o.votes for o in options)
    
    # Check if this browser has already voted in this room
    cookie_key = f"voted_{room_id}"
    has_voted = (request.cookies.get(cookie_key) == 'true' or session.get(cookie_key) == True)
    
    return render_template(
        'vote/room.html', 
        room=room_obj, 
        options=options, 
        total_votes=total_votes,
        has_voted=has_voted
    )

@vote_bp.route('/vote/<room_id>/cast', methods=['POST'])
def cast_vote(room_id):
    room_obj = VoteRoom.query.get_or_404(room_id)
    option_id = request.form.get('option_id')
    
    cookie_key = f"voted_{room_id}"
    has_voted = (request.cookies.get(cookie_key) == 'true' or session.get(cookie_key) == True)
    
    if has_voted:
        flash('您已經在此房間投過票囉！每一房僅限投一票。', 'warning')
        return redirect(url_for('vote.room', room_id=room_id))
        
    if not option_id:
        flash('請選擇一個餐廳進行投票！', 'error')
        return redirect(url_for('vote.room', room_id=room_id))
        
    option = VoteOption.query.filter_by(room_id=room_id, id=option_id).first()
    if not option:
        flash('無效的投票選項！', 'error')
        return redirect(url_for('vote.room', room_id=room_id))
        
    # Increment vote
    option.votes += 1
    db.session.commit()
    
    # Set cookies & session
    session[cookie_key] = True
    response = make_response(redirect(url_for('vote.room', room_id=room_id)))
    response.set_cookie(cookie_key, 'true', max_age=60*60*24*7) # 1 week
    
    flash('投票成功！感謝您的參與 🎉', 'success')
    return response

@vote_bp.route('/vote/<room_id>/data')
def room_data(room_id):
    # API for AJAX pooling to get real-time charts without reloading
    room_obj = VoteRoom.query.get(room_id)
    if not room_obj:
        return jsonify({'error': 'Room not found'}), 404
        
    options = VoteOption.query.filter_by(room_id=room_id).all()
    total_votes = sum(o.votes for o in options)
    
    data = []
    for opt in options:
        pct = round((opt.votes / total_votes * 100), 1) if total_votes > 0 else 0
        data.append({
            'option_id': opt.id,
            'restaurant_name': opt.restaurant.name,
            'votes': opt.votes,
            'percentage': pct
        })
        
    return jsonify({
        'room_title': room_obj.title,
        'total_votes': total_votes,
        'options': data
    })

@vote_bp.route('/vote/<room_id>/delete', methods=['POST'])
def delete_room(room_id):
    room_obj = VoteRoom.query.get_or_404(room_id)
    db.session.delete(room_obj)
    db.session.commit()
    flash('投票房間已成功刪除！', 'success')
    return redirect(url_for('vote.lobby'))
