"""
app/__init__.py

Flask 工廠函數（Application Factory）與應用程式初始化。
在這裡配置 SQLite、SQLAlchemy、Flask-Login，並註冊所有 Blueprints。
"""
import os
from flask import Flask
from flask_login import LoginManager, UserMixin
from app.models import db
from app.routes.favorite_routes import favorite_bp
from app.routes.history_routes import history_bp

def create_app():
    """建立並設定 Flask 應用程式實例 (App Factory)"""
    app = Flask(__name__)

    # --- 基本安全與 Session 配置 ---
    app.config['SECRET_KEY'] = 'lets-just-eat-secret-key-super-secure'

    # --- SQLite 資料庫配置 ---
    # 確保 instance 目錄存在
    instance_path = os.path.join(app.root_path, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_file_path = os.path.join(instance_path, 'database.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 為了簡化 MVP 開發與展示測試，啟用 Flask-Login 繞過配置，免去註冊/登入的繁瑣步驟
    app.config['LOGIN_DISABLED'] = True

    # --- 初始化資料庫 ---
    db.init_app(app)

    # --- 初始化 Flask-Login 機制 ---
    login_manager = LoginManager()
    login_manager.init_app(app)

    class DummyUser(UserMixin):
        """用於繞過或提供預設登入狀態的 Mock 使用者類別"""
        def __init__(self, id):
            self.id = id
            self.username = "MockUser"

    @login_manager.user_loader
    def load_user(user_id):
        return DummyUser(user_id)

    # --- 註冊 Blueprints ---
    app.register_blueprint(favorite_bp)
    app.register_blueprint(history_bp)

    # --- 首頁 (/) 簡易路由：提供超方便的互動測試面板 ---
    @app.route('/')
    def index():
        from flask import render_template_string
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}首頁 - 隨便吃什麼都好{% endblock %}
        {% block content %}
        <div class="row justify-content-center py-5">
            <div class="col-lg-10 col-xl-8">
                <!-- 歡迎看板 -->
                <div class="card glass-card p-5 text-center mb-5">
                    <h1 class="display-4 fw-bold mb-3">
                        <span class="bg-gradient text-transparent" style="background: var(--primary-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            <i class="bi bi-dice-5 me-2"></i>隨便吃什麼都好
                        </span>
                    </h1>
                    <p class="lead text-muted mb-4">功能整合成功！這是您的個人美食推薦與口袋名單助手系統。</p>
                    <div class="d-flex justify-content-center gap-3 flex-wrap">
                        <a href="/favorites" class="btn btn-gradient px-4"><i class="bi bi-heart-fill me-2"></i>我的收藏清單</a>
                        <a href="/history" class="btn btn-outline-custom px-4"><i class="bi bi-clock-history me-2"></i>查看抽選歷史</a>
                    </div>
                </div>

                <!-- 測試控制面板 -->
                <div class="row g-4">
                    <!-- 新增收藏測試表單 -->
                    <div class="col-md-6">
                        <div class="card glass-card h-100 p-4 border border-secondary-subtle border-opacity-10" style="background: rgba(255,255,255,0.02);">
                            <div class="d-flex align-items-center mb-3">
                                <div class="bg-danger bg-opacity-10 p-2 rounded-circle me-3">
                                    <i class="bi bi-heart text-danger fs-4"></i>
                                </div>
                                <h4 class="fw-bold mb-0 text-light">新增收藏餐廳</h4>
                            </div>
                            <p class="text-muted small">模擬向資料庫中寫入一筆收藏口袋名單</p>
                            
                            <form action="/favorites/add" method="POST">
                                <div class="mb-3">
                                    <label class="form-label text-muted small">餐廳名稱 <span class="text-danger">*</span></label>
                                    <input type="text" name="restaurant_name" class="form-control bg-dark border-secondary text-white rounded-3 py-2" placeholder="例如：極品豚骨拉麵" value="極品豚骨拉麵" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label text-muted small">餐點類型</label>
                                    <input type="text" name="category" class="form-control bg-dark border-secondary text-white rounded-3 py-2" placeholder="例如：日式" value="日式">
                                </div>
                                <div class="row g-2 mb-3">
                                    <div class="col-6">
                                        <label class="form-label text-muted small">評分 (1.0 ~ 5.0)</label>
                                        <input type="number" step="0.1" min="1.0" max="5.0" name="rating" class="form-control bg-dark border-secondary text-white rounded-3 py-2" placeholder="例如：4.8" value="4.8">
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label text-muted small">地址</label>
                                        <input type="text" name="address" class="form-control bg-dark border-secondary text-white rounded-3 py-2" placeholder="例如：台北市..." value="台中市西區公益路 100 號">
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-gradient w-100 py-2 mt-2">
                                    <i class="bi bi-plus-circle me-2"></i>寫入收藏資料表
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- 新增歷史紀錄測試表單 -->
                    <div class="col-md-6">
                        <div class="card glass-card h-100 p-4 border border-secondary-subtle border-opacity-10" style="background: rgba(255,255,255,0.02);">
                            <div class="d-flex align-items-center mb-3">
                                <div class="bg-primary bg-opacity-10 p-2 rounded-circle me-3">
                                    <i class="bi bi-clock-history text-primary fs-4"></i>
                                </div>
                                <h4 class="fw-bold mb-0 text-light">模擬系統抽選紀錄</h4>
                            </div>
                            <p class="text-muted small">模擬點擊「抽！」之後，系統於背景寫入的推薦紀錄</p>
                            
                            <form action="/history/add" method="POST">
                                <div class="mb-3">
                                    <label class="form-label text-muted small">餐廳名稱 <span class="text-danger">*</span></label>
                                    <input type="text" name="restaurant_name" class="form-control bg-dark border-secondary text-white rounded-3 py-2" placeholder="例如：麻辣鴛鴦鍋" value="麻辣鴛鴦鍋" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label text-muted small">餐點類型</label>
                                    <input type="text" name="category" class="form-control bg-dark border-secondary text-white rounded-3 py-2" placeholder="例如：火鍋" value="火鍋">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label text-muted small">評分 (1.0 ~ 5.0)</label>
                                    <input type="number" step="0.1" min="1.0" max="5.0" name="rating" class="form-control bg-dark border-secondary text-white rounded-3 py-2" placeholder="例如：4.5" value="4.5">
                                </div>
                                <button type="submit" class="btn btn-outline-primary w-100 py-2 mt-4" style="border-radius: 8px;">
                                    <i class="bi bi-dice-5 me-2"></i>寫入歷史紀錄表
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endblock %}
        """)

    return app
