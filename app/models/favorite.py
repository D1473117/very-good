from datetime import datetime
from app.models import db

class Favorite(db.Model):
    """
    Favorite Model 代表使用者的收藏餐廳。
    直接存儲餐廳詳細資訊（名稱、類型、評分、地址與收藏時間）。
    """
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Favorite {self.restaurant_name} (ID: {self.id})>"

    # ==========================================
    # CRUD Operations
    # ==========================================

    @classmethod
    def create(cls, restaurant_name, category=None, rating=None, address=None):
        """
        新增收藏餐廳。
        
        :param restaurant_name: 餐廳名稱 (必填)
        :param category: 餐點類型 (選填)
        :param rating: 餐廳評分 (選填)
        :param address: 餐廳地址 (選填)
        :return: 新增的 Favorite 物件
        """
        try:
            favorite = cls(
                restaurant_name=restaurant_name,
                category=category,
                rating=rating,
                address=address
            )
            db.session.add(favorite)
            db.session.commit()
            return favorite
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def delete(cls, id):
        """
        根據 ID 刪除指定的收藏餐廳。
        
        :param id: 收藏 ID (必填)
        :return: bool, 刪除成功回傳 True，若不存在則回傳 False
        """
        try:
            favorite = cls.query.get(id)
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_all(cls):
        """
        查詢所有收藏餐廳，按收藏時間降序 (最新收藏的在最前面)。
        
        :return: list[Favorite]
        """
        try:
            return cls.query.order_by(cls.created_at.desc()).all()
        except Exception as e:
            raise e

    @classmethod
    def get_by_id(cls, id):
        """
        根據 ID 取得單筆收藏詳細資訊。
        
        :param id: 收藏 ID (必填)
        :return: Favorite 物件，若不存在則回傳 None
        """
        try:
            return cls.query.get(id)
        except Exception as e:
            raise e

    @classmethod
    def update(cls, id, **kwargs):
        """
        更新特定 ID 收藏餐廳的欄位資訊。
        
        :param id: 收藏 ID (必填)
        :param kwargs: 動態欄位與其對應值 (例如 category='義式', rating=4.5)
        :return: 更新後的 Favorite 物件，若不存在則回傳 None
        """
        try:
            favorite = cls.query.get(id)
            if favorite:
                for key, value in kwargs.items():
                    if hasattr(favorite, key):
                        setattr(favorite, key, value)
                db.session.commit()
                return favorite
            return None
        except Exception as e:
            db.session.rollback()
            raise e
