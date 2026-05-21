from datetime import datetime
from app.models import db

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('user_favorites', cascade="all, delete-orphan", lazy=True))
    restaurant = db.relationship('Restaurant', backref=db.backref('restaurant_favorites', cascade="all, delete-orphan", lazy=True))

    def __repr__(self):
        return f"<Favorite User:{self.user_id} Restaurant:{self.restaurant_id}>"
