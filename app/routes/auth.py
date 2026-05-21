from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not password:
            flash('請填寫所有必要欄位！', 'error')
            return render_template('auth/register.html')
            
        if len(password) < 6:
            flash('密碼長度必須至少為 6 個字元！', 'error')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('密碼與確認密碼不符！', 'error')
            return render_template('auth/register.html')
            
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('該使用者名稱已被註冊！', 'error')
            return render_template('auth/register.html')
            
        # Create user
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log user in
        login_user(new_user)
        flash('註冊成功！歡迎來到隨便吃什麼都好 🥳', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('auth/register.html')

@auth_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('使用者名稱或密碼錯誤！', 'error')
            return render_template('auth/login.html')
            
        login_user(user, remember=remember)
        flash(f'登入成功！歡迎回來，{username}！ 👋', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('auth/login.html')

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    logout_user()
    flash('您已成功登出！期待下次與您相見 💫', 'success')
    return redirect(url_for('main.index'))
