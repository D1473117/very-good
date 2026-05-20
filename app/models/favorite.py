from datetime import datetime
from app.models import db

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 建立多對一關係
    user = db.relationship('User', backref=db.backref('favorites', lazy=True, cascade='all, delete-orphan'))
    restaurant = db.relationship('Restaurant', backref=db.backref('favorited_by', lazy=True))

    # 聯合唯一限制
    __table_args__ = (
        db.UniqueConstraint('user_id', 'restaurant_id', name='uq_user_restaurant_favorite'),
    )

    def __repr__(self):
        return f"<Favorite User:{self.user_id} Restaurant:{self.restaurant_id}>"

    # ==========================================
    # CRUD & 業務方法封裝
    # ==========================================

    @classmethod
    def create(cls, user_id, restaurant_id):
        """新增收藏，若已存在則直接回傳該紀錄"""
        existing = cls.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
        if existing:
            return existing
        favorite = cls(user_id=user_id, restaurant_id=restaurant_id)
        db.session.add(favorite)
        db.session.commit()
        return favorite

    @classmethod
    def delete(cls, user_id, restaurant_id):
        """取消收藏"""
        favorite = cls.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return True
        return False

    @classmethod
    def get_by_user(cls, user_id):
        """取得特定使用者的所有收藏，並以時間降序排序"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def is_favorited(cls, user_id, restaurant_id):
        """檢查特定餐廳是否已被使用者收藏"""
        return cls.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first() is not None
