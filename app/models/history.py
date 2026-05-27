"""
app/models/history.py

History Model — 歷史推薦紀錄資料表

資料表名稱：history
資料庫：SQLite（instance/database.db）
ORM：Flask-SQLAlchemy

欄位：
    id              INTEGER  PRIMARY KEY AUTOINCREMENT
    restaurant_name VARCHAR(100) NOT NULL
    category        VARCHAR(50)
    rating          FLOAT  (1.0 ~ 5.0)
    recommended_at  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL

CRUD 方法：
    History.create(...)           → 新增歷史紀錄（系統自動呼叫）
    History.get_all(limit, offset)→ 查詢歷史紀錄（支援分頁）
    History.get_by_id(id)         → 查詢單筆
    History.delete(id)            → 刪除單筆紀錄
    History.clear_all()           → 清空全部歷史紀錄
"""
from datetime import datetime
from app.models import db


class History(db.Model):
    """歷史推薦紀錄資料表 ORM Model

    系統每次進行隨機推薦時，自動寫入一筆紀錄。
    採用非正規化設計，直接儲存餐廳快照資料。
    """

    __tablename__ = 'history'

    # ----- 欄位定義 -----
    id              = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    restaurant_name = db.Column(db.String(100), nullable=False)
    category        = db.Column(db.String(50),  nullable=True)
    rating          = db.Column(db.Float,       nullable=True)
    recommended_at  = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<History id={self.id} name='{self.restaurant_name}' at={self.recommended_at}>"

    def to_dict(self):
        """將物件序列化為字典，方便傳入 Jinja2 模板或 JSON 回應

        :return: dict
        """
        return {
            'id':              self.id,
            'restaurant_name': self.restaurant_name,
            'category':        self.category,
            'rating':          self.rating,
            'recommended_at':  self.recommended_at.strftime('%Y-%m-%d %H:%M') if self.recommended_at else None,
        }

    # ==========================================
    # CRUD 操作
    # ==========================================

    @classmethod
    def create(cls, restaurant_name, category=None, rating=None):
        """新增一筆推薦歷史紀錄

        系統在完成隨機抽選後自動呼叫此方法，
        將當次推薦的餐廳快照寫入 history 資料表。

        使用範例：
            history = History.create(
                restaurant_name='好吃拉麵',
                category='日式',
                rating=4.5,
            )

        :param restaurant_name: 餐廳名稱（必填）
        :param category:        餐點類型（選填）
        :param rating:          評分 1.0~5.0（選填）
        :return: History 實例；發生例外時回傳 None
        """
        try:
            history = cls(
                restaurant_name=restaurant_name,
                category=category,
                rating=rating,
            )
            db.session.add(history)
            db.session.commit()
            return history
        except Exception as e:
            db.session.rollback()
            print(f"[History.create] 錯誤：{e}")
            return None

    @classmethod
    def get_all(cls, limit=None, offset=None):
        """取得所有歷史推薦紀錄，依推薦時間降序排列（最新在最前）

        支援分頁參數，適用於歷史紀錄列表頁面的分頁顯示。

        使用範例：
            # 取得第 1 頁（每頁 10 筆）
            page = 1
            histories = History.get_all(limit=10, offset=(page-1)*10)

        :param limit:  每頁顯示筆數（選填，None 表示不限制）
        :param offset: 跳過筆數（選填，None 表示從第 1 筆開始）
        :return: List[History]；發生例外時回傳空清單 []
        """
        try:
            query = cls.query.order_by(cls.recommended_at.desc())
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)
            return query.all()
        except Exception as e:
            print(f"[History.get_all] 錯誤：{e}")
            return []

    @classmethod
    def get_by_id(cls, history_id):
        """依主鍵 ID 取得單筆歷史推薦紀錄

        使用範例：
            record = History.get_by_id(5)
            if record:
                print(record.restaurant_name)

        :param history_id: 歷史紀錄 ID（整數）
        :return: History 實例；找不到或例外時回傳 None
        """
        try:
            return cls.query.get(history_id)
        except Exception as e:
            print(f"[History.get_by_id] 錯誤：{e}")
            return None

    @classmethod
    def delete(cls, history_id):
        """刪除指定歷史紀錄

        使用範例：
            success = History.delete(5)

        :param history_id: 歷史紀錄 ID（整數）
        :return: True 刪除成功；False 找不到紀錄或發生例外
        """
        try:
            history = cls.query.get(history_id)
            if not history:
                return False
            db.session.delete(history)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[History.delete] 錯誤：{e}")
            return False

    @classmethod
    def clear_all(cls):
        """清空所有歷史推薦紀錄

        由使用者在個人中心點擊「清空歷史紀錄」按鈕後觸發。

        使用範例：
            success = History.clear_all()
            if success:
                flash('歷史紀錄已清空')

        :return: True 清空成功；False 發生例外
        """
        try:
            cls.query.delete()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[History.clear_all] 錯誤：{e}")
            return False
