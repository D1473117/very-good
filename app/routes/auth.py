from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    處理使用者註冊頁面與註冊邏輯。
    
    GET: 渲染 templates/auth/register.html 註冊頁面。
    POST: 接收 username, password, confirm_password。
          驗證格式與重覆性，密碼雜湊後寫入 user 表。
          成功後重導向至 /auth/login。
    """
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    處理使用者登入頁面與登入邏輯。
    
    GET: 渲染 templates/auth/login.html 登入頁面。
    POST: 接收 username, password。
          驗證密碼，若成功則調用 login_user() 建立 Session。
          成功後重導向至首頁 /。
    """
    pass

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    處理使用者登出邏輯。
    
    調用 logout_user() 清除登入狀態的 Session。
    重導向至首頁 /。
    """
    pass
