"""
app/models/favorite.py

Favorite Model — 收藏餐廳資料表

資料表名稱：favorites
資料庫：SQLite（instance/database.db）
ORM：Flask-SQLAlchemy

欄位：
    id              INTEGER  PRIMARY KEY AUTOINCREMENT
    restaurant_name VARCHAR(100) NOT NULL
    category        VARCHAR(50)
    rating          FLOAT  (1.0 ~ 5.0)
    address         VARCHAR(200)
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL

CRUD 方法：
    Favorite.create(...)    → 新增收藏
    Favorite.get_all()      → 查詢全部收藏（降序）
    Favorite.get_by_id(id)  → 查詢單筆
    Favorite.update(id, {}) → 更新收藏資料
    Favorite.delete(id)     → 刪除收藏
"""
from datetime import datetime
from app.models import db


class Favorite(db.Model):
    """收藏餐廳資料表 ORM Model

    採用非正規化設計，直接儲存餐廳快照資料，
    不依賴外部 restaurants 資料表，降低查詢複雜度。
    """

    __tablename__ = 'favorites'

    # ----- 欄位定義 -----
    id              = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    restaurant_name = db.Column(db.String(100),  nullable=False)
    category        = db.Column(db.String(50),   nullable=True)
    rating          = db.Column(db.Float,        nullable=True)
    address         = db.Column(db.String(200),  nullable=True)
    created_at      = db.Column(db.DateTime,     default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Favorite id={self.id} name='{self.restaurant_name}'>"

    def to_dict(self):
        """將物件序列化為字典，方便傳入 Jinja2 模板或 JSON 回應

        :return: dict
        """
        return {
            'id':              self.id,
            'restaurant_name': self.restaurant_name,
            'category':        self.category,
            'rating':          self.rating,
            'address':         self.address,
            'created_at':      self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
        }

    # ==========================================
    # CRUD 操作
    # ==========================================

    @classmethod
    def create(cls, restaurant_name, category=None, rating=None, address=None):
        """新增一筆收藏紀錄

        使用範例：
            fav = Favorite.create(
                restaurant_name='好吃拉麵',
                category='日式',
                rating=4.5,
                address='台中市西區...',
            )

        :param restaurant_name: 餐廳名稱（必填）
        :param category:        餐點類型，例如「日式」、「中式」（選填）
        :param rating:          評分 1.0~5.0（選填）
        :param address:         餐廳地址（選填）
        :return: Favorite 實例；發生例外時回傳 None
        """
        try:
            favorite = cls(
                restaurant_name=restaurant_name,
                category=category,
                rating=rating,
                address=address,
            )
            db.session.add(favorite)
            db.session.commit()
            return favorite
        except Exception as e:
            db.session.rollback()
            print(f"[Favorite.create] 錯誤：{e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有收藏紀錄，依收藏時間降序排列（最新在最前）

        使用範例：
            favorites = Favorite.get_all()
            for fav in favorites:
                print(fav.restaurant_name)

        :return: List[Favorite]；發生例外時回傳空清單 []
        """
        try:
            return cls.query.order_by(cls.created_at.desc()).all()
        except Exception as e:
            print(f"[Favorite.get_all] 錯誤：{e}")
            return []

    @classmethod
    def get_by_id(cls, favorite_id):
        """依主鍵 ID 取得單筆收藏紀錄

        使用範例：
            fav = Favorite.get_by_id(3)
            if fav:
                print(fav.restaurant_name)

        :param favorite_id: 收藏紀錄 ID（整數）
        :return: Favorite 實例；找不到或例外時回傳 None
        """
        try:
            return cls.query.get(favorite_id)
        except Exception as e:
            print(f"[Favorite.get_by_id] 錯誤：{e}")
            return None

    @classmethod
    def update(cls, favorite_id, data: dict):
        """更新指定收藏紀錄的欄位

        使用範例：
            Favorite.update(3, {'rating': 4.8, 'category': '台式'})

        :param favorite_id: 收藏紀錄 ID（整數）
        :param data:        要更新的欄位字典（僅接受合法欄位名稱）
        :return: 更新後的 Favorite 實例；找不到或例外時回傳 None
        """
        try:
            favorite = cls.query.get(favorite_id)
            if not favorite:
                return None
            allowed_fields = {'restaurant_name', 'category', 'rating', 'address'}
            for key, value in data.items():
                if key in allowed_fields:
                    setattr(favorite, key, value)
            db.session.commit()
            return favorite
        except Exception as e:
            db.session.rollback()
            print(f"[Favorite.update] 錯誤：{e}")
            return None

    @classmethod
    def delete(cls, favorite_id):
        """刪除指定收藏紀錄

        使用範例：
            success = Favorite.delete(3)
            if success:
                flash('收藏已移除')

        :param favorite_id: 收藏紀錄 ID（整數）
        :return: True 刪除成功；False 找不到紀錄或發生例外
        """
        try:
            favorite = cls.query.get(favorite_id)
            if not favorite:
                return False
            db.session.delete(favorite)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Favorite.delete] 錯誤：{e}")
            return False
