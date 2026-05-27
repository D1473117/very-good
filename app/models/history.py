from datetime import datetime
from app.models import db

class History(db.Model):
    """
    History Model 代表隨機推薦的歷史紀錄。
    直接存儲每次抽選推薦出來的餐廳詳細資訊（名稱、類型、評分與推薦時間）。
    """
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    recommended_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<History {self.restaurant_name} (ID: {self.id})>"

    # ==========================================
    # CRUD Operations
    # ==========================================

    @classmethod
    def create(cls, restaurant_name, category=None, rating=None):
        """
        新增推薦歷史紀錄。
        
        :param restaurant_name: 餐廳名稱 (必填)
        :param category: 餐點類型 (選填)
        :param rating: 餐廳評分 (選填)
        :return: 新增的 History 物件
        """
        try:
            record = cls(
                restaurant_name=restaurant_name,
                category=category,
                rating=rating
            )
            db.session.add(record)
            db.session.commit()
            return record
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_all(cls):
        """
        查詢所有推薦歷史紀錄，按推薦時間降序 (最新推薦的在最前面)。
        
        :return: list[History]
        """
        try:
            return cls.query.order_by(cls.recommended_at.desc()).all()
        except Exception as e:
            raise e

    @classmethod
    def get_by_id(cls, id):
        """
        根據 ID 取得單筆歷史紀錄詳細資訊。
        
        :param id: 歷史紀錄 ID (必填)
        :return: History 物件，若不存在則回傳 None
        """
        try:
            return cls.query.get(id)
        except Exception as e:
            raise e

    @classmethod
    def update(cls, id, **kwargs):
        """
        更新特定 ID 歷史紀錄的欄位資訊。
        
        :param id: 歷史紀錄 ID (必填)
        :param kwargs: 動態欄位與其對應值 (例如 category='日式', rating=4.8)
        :return: 更新後的 History 物件，若不存在則回傳 None
        """
        try:
            record = cls.query.get(id)
            if record:
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                db.session.commit()
                return record
            return None
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def delete(cls, id):
        """
        根據 ID 刪除指定的歷史紀錄。
        
        :param id: 歷史紀錄 ID (必填)
        :return: bool, 刪除成功回傳 True，若不存在則回傳 False
        """
        try:
            record = cls.query.get(id)
            if record:
                db.session.delete(record)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
