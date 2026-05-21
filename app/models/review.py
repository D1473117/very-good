from datetime import datetime
from app.models import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('user_reviews', cascade="all, delete-orphan", lazy=True))
    restaurant = db.relationship('Restaurant', backref=db.backref('restaurant_reviews', cascade="all, delete-orphan", lazy=True))

    def __repr__(self):
        return f"<Review User:{self.user_id} Restaurant:{self.restaurant_id} Rating:{self.rating}>"
