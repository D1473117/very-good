from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import db

class History(db.Model):
    """
    History Model
    負責處理推薦歷史紀錄的資料庫操作
    """
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    recommended_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, **kwargs):
        """
        新增歷史紀錄
        
        :param kwargs: 餐廳資料 (restaurant_name, category, rating)
        :return: 成功時回傳 History 物件，失敗回傳 None
        """
        try:
            new_history = cls(**kwargs)
            db.session.add(new_history)
            db.session.commit()
            return new_history
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error creating history: {e}")
            return None

    @classmethod
    def get_all(cls):
        """
        取得所有歷史紀錄，依照推薦時間遞減排序
        
        :return: History 物件列表，失敗回傳空列表
        """
        try:
            return cls.query.order_by(cls.recommended_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error getting history: {e}")
            return []
