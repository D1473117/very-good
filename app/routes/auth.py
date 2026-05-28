from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import create_user, check_user_credentials

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    處理會員註冊請求。
    
    GET: 渲染註冊頁面 (register.html)。
    POST: 接收註冊表單，驗證密碼強度及一致性，成功後透過 create_user() 寫入資料庫，並自動為用戶建立 Session 登入狀態。
    """
    if 'user_id' in session:
        return redirect(url_for('recommendation.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Basic input validation
        if not username or not password:
            flash('請輸入帳號和密碼！', 'danger')
            return render_template('register.html')
            
        if len(password) < 6:
            flash('密碼長度需至少為 6 個字元！', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('兩次輸入的密碼不一致！', 'danger')
            return render_template('register.html')
            
        try:
            user_id = create_user(username, password)
            if user_id:
                session['user_id'] = user_id
                session['username'] = username
                flash('註冊成功！已自動為您登入。', 'success')
                return redirect(url_for('recommendation.index'))
            else:
                flash('帳號已被註冊，請換一個名字！', 'danger')
        except Exception as e:
            print(f"Error registering user: {e}")
            flash('註冊時發生系統異常，請稍後再試！', 'danger')
            
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    處理會員登入請求。
    
    GET: 渲染登入頁面 (login.html)。
    POST: 接收帳號密碼，呼叫 check_user_credentials() 進行 PBKDF2 雜湊密碼驗證，通過後將用戶 ID 及帳號寫入 Session。
    """
    if 'user_id' in session:
        return redirect(url_for('recommendation.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('請輸入帳號和密碼！', 'danger')
            return render_template('login.html')
            
        try:
            user = check_user_credentials(username, password)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'歡迎回來，{user["username"]}！', 'success')
                return redirect(url_for('recommendation.index'))
            else:
                flash('帳號或密碼錯誤，請再試一次！', 'danger')
        except Exception as e:
            print(f"Error logging in user: {e}")
            flash('登入時發生系統異常，請稍後再試！', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """
    處理會員登出請求。
    
    清除 Session 中所有用戶認證狀態，並重導向回系統首頁。
    """
    session.clear()
    flash('您已成功登出。', 'success')
    return redirect(url_for('recommendation.index'))

