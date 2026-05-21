from app.models import db

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    default_radius = db.Column(db.Integer, default=3000, nullable=False)
    default_min_price = db.Column(db.Integer, default=1, nullable=False)
    default_max_price = db.Column(db.Integer, default=3, nullable=False)
    favorite_cuisines = db.Column(db.Text, default='[]', nullable=False) # JSON list

    # Relationships
    user = db.relationship('User', backref=db.backref('preferences', cascade="all, delete-orphan", uselist=False, lazy=True))

    def __repr__(self):
        return f"<UserPreference User:{self.user_id} Session:{self.session_id}>"
