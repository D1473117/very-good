from datetime import datetime
import uuid
from app.models import db

class VoteRoom(db.Model):
    __tablename__ = 'vote_rooms'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    options = db.relationship('VoteOption', backref='room', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<VoteRoom {self.id} {self.title}>"

class VoteOption(db.Model):
    __tablename__ = 'vote_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.String(36), db.ForeignKey('vote_rooms.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    votes = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    restaurant = db.relationship('Restaurant', backref=db.backref('vote_options', cascade="all, delete-orphan", lazy=True))

    def __repr__(self):
        return f"<VoteOption Room:{self.room_id} Restaurant:{self.restaurant_id} Votes:{self.votes}>"
