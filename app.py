from flask import Flask
from app.routes import auth_bp, favorite_bp, recommendation_bp, review_bp
from app.models.restaurant import init_db

def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
    app.config['SECRET_KEY'] = 'dev_secret_key'
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(review_bp)
    
    # Initialize the database schema and dummy data once at startup
    init_db()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
