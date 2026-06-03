from app.models import db

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    price_level = db.Column(db.Integer, nullable=False)  # 1: 平價, 2: 中等, 3: 昂貴, 4: 奢華
    distance = db.Column(db.Integer, nullable=False)    # in meters
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'rating': self.rating,
            'address': self.address,
            'price_level': self.price_level,
            'distance': self.distance,
            'lat': self.lat,
            'lng': self.lng
        }
