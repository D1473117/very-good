from datetime import datetime
from app.models import db

class RecommendationHistory(db.Model):
    __tablename__ = 'recommendation_histories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    recommended_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 建立多對一關係
    user = db.relationship('User', backref=db.backref('recommendation_histories', lazy=True, cascade='all, delete-orphan'))
    restaurant = db.relationship('Restaurant', backref=db.backref('recommendation_histories', lazy=True))

    def __repr__(self):
        return f"<RecommendationHistory User:{self.user_id} Restaurant:{self.restaurant_id} Time:{self.recommended_at}>"

    # ==========================================
    # CRUD & 業務方法封裝
    # ==========================================

    @classmethod
    def create(cls, user_id, restaurant_id):
        """系統自動寫入推薦歷史紀錄

        :param user_id: 使用者 ID
        :param restaurant_id: 餐廳 ID
        :return: RecommendationHistory 實例，若發生異常則回傳 None
        """
        try:
            history = cls(user_id=user_id, restaurant_id=restaurant_id)
            db.session.add(history)
            db.session.commit()
            return history
        except Exception as e:
            db.session.rollback()
            print(f"Error in RecommendationHistory.create: {e}")
            return None

    @classmethod
    def get_by_user(cls, user_id, limit=None, offset=None):
        """取得特定使用者的歷史推薦紀錄，支援分頁與時間降序

        :param user_id: 使用者 ID
        :param limit: 回傳資料筆數限制 (選填)
        :param offset: 跳過資料筆數 (選填)
        :return: RecommendationHistory 實例清單，若發生異常則回傳空清單
        """
        try:
            query = cls.query.filter_by(user_id=user_id).order_by(cls.recommended_at.desc())
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            return query.all()
        except Exception as e:
            print(f"Error in RecommendationHistory.get_by_user: {e}")
            return []

    @classmethod
    def clear_user_history(cls, user_id):
        """清空特定使用者的所有推薦歷史

        :param user_id: 使用者 ID
        :return: bool (清空是否成功)
        """
        try:
            cls.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error in RecommendationHistory.clear_user_history: {e}")
            return False

