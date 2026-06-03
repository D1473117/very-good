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

    # Register blueprints
    from app.routes.favorite_routes import favorite_bp
    from app.routes.history_routes import history_bp
    from app.routes.main import main_bp
    from app.routes.restaurant import restaurant_bp
    from app.routes.voting import voting_bp
    
    app.register_blueprint(favorite_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(voting_bp)



    return app
