from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them on the metadata
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.favorite import Favorite
from app.models.review import Review
from app.models.history import SpinHistory
from app.models.preference import UserPreference
from app.models.vote import VoteRoom, VoteOption
