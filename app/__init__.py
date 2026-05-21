import os
from flask import Flask
from app.models import db
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '請先登入後再進行此操作！'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lets-just-eat-secret-key-12345')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(app.instance_path, 'database.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.restaurant import restaurant_bp
    from app.routes.profile import profile_bp
    from app.routes.vote import vote_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(vote_bp)

    # User loader for Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
