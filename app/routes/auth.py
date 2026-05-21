from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    處理會員註冊請求。
    
    GET: 渲染註冊頁面 (register.html)。
    POST: 接收註冊表單，驗證密碼強度及一致性，成功後透過 create_user() 寫入資料庫，並自動為用戶建立 Session 登入狀態。
    """
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    處理會員登入請求。
    
    GET: 渲染登入頁面 (login.html)。
    POST: 接收帳號密碼，呼叫 check_user_credentials() 進行 PBKDF2 雜湊密碼驗證，通過後將用戶 ID 及帳號寫入 Session。
    """
    pass

@auth_bp.route('/logout')
def logout():
    """
    處理會員登出請求。
    
    清除 Session 中所有用戶認證狀態，並重導向回系統首頁。
    """
    pass
