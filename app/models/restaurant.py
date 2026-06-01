from app.models import db

class Restaurant(db.Model):
    """
    Restaurant Model 代表系統中可供抽選的餐廳。
    """
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)      # e.g., 中式, 日式, 韓式, 美式, 義式, 火鍋, 素食, 飲料, 甜點
    price_range = db.Column(db.String(50), nullable=True)     # e.g., $50 以下, $50-$150, $150-$300, $300+
    rating = db.Column(db.Float, nullable=True)               # 0.0 ~ 5.0
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    operating_hours = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)      # 餐廳封面圖 URL
    google_maps_url = db.Column(db.String(500), nullable=True) # Google 地圖內嵌或外連
    latitude = db.Column(db.Float, nullable=True)             # GPS 緯度
    longitude = db.Column(db.Float, nullable=True)            # GPS 經度

    def __repr__(self):
        return f"<Restaurant {self.name} (ID: {self.id})>"

    @classmethod
    def get_all(cls):
        """查詢所有餐廳"""
        try:
            return cls.query.all()
        except Exception as e:
            raise e

    @classmethod
    def get_by_id(cls, id):
        """根據 ID 取得單筆餐廳資訊"""
        try:
            return cls.query.get(id)
        except Exception as e:
            raise e
