from flask import Flask
from app.routes import main_bp

def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
    app.config['SECRET_KEY'] = 'dev_secret_key'
    
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
