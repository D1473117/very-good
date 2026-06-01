from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered with db
from app.models.favorite import Favorite
from app.models.history import History
from app.models.restaurant import Restaurant

