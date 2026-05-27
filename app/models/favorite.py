from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import db

class Favorite(db.Model):
    """
    Favorite Model
    負責處理收藏餐廳的資料庫操作
    """
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, **kwargs):
        """
        新增收藏紀錄
        
        :param kwargs: 餐廳資料 (restaurant_name, category, rating, address)
        :return: 成功時回傳 Favorite 物件，失敗回傳 None
        """
        try:
            new_favorite = cls(**kwargs)
            db.session.add(new_favorite)
            db.session.commit()
            return new_favorite
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error creating favorite: {e}")
            return None

    @classmethod
    def get_all(cls):
        """
        取得全部收藏紀錄，依照加入時間遞減排序
        
        :return: Favorite 物件列表，失敗回傳空列表
        """
        try:
            return cls.query.order_by(cls.created_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error getting favorites: {e}")
            return []

    @classmethod
    def delete(cls, record_id):
        """
        刪除收藏紀錄
        
        :param record_id: 收藏紀錄的 ID
        :return: 刪除成功回傳 True，否則回傳 False
        """
        try:
            favorite = cls.query.get(record_id)
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error deleting favorite: {e}")
            return False
