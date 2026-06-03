from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered with db
from app.models.favorite import Favorite
from app.models.history import History
from app.models.restaurant import Restaurant
from app.models.voting_room import VotingRoom
from app.models.room_candidate import RoomCandidate


