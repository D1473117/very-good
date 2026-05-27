import os
from flask import Flask
from app.models import db

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev-secret-key',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'database.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)

    # Register blueprints (Focusing on F-05 favorites and history)
    from app.routes.favorite_routes import favorite_bp
    from app.routes.history_routes import history_bp
    
    app.register_blueprint(favorite_bp)
    app.register_blueprint(history_bp)

    # A simple home route to redirect to favorites for easy testing
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('favorite.list_favorites'))

    return app
