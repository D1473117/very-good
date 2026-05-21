from datetime import datetime
from app.models import db

class SpinHistory(db.Model):
    __tablename__ = 'spin_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    distance = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('spin_history', cascade="all, delete-orphan", lazy=True))
    restaurant = db.relationship('Restaurant', backref=db.backref('spin_history', cascade="all, delete-orphan", lazy=True))

    def __repr__(self):
        return f"<SpinHistory User:{self.user_id} Restaurant:{self.restaurant_id}>"
