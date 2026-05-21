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
    return render_template('vote/lobby.html', rooms=rooms)

@vote_bp.route('/vote/create', methods=['POST'])
def create_room():
    title = request.form.get('title', '').strip()
    if not title:
        title = "今天吃什麼？美味對決！"
        
    # Pick 4 random restaurants from the database as candidates
    restaurants = Restaurant.query.all()
    if len(restaurants) < 2:
        flash('資料庫餐廳數量不足，無法建立投票！', 'error')
        return redirect(url_for('vote.lobby'))
        
    candidates = random.sample(restaurants, min(4, len(restaurants)))
    
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
