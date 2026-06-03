import uuid
from datetime import datetime
from app.models import db

class VotingRoom(db.Model):
    """
    VotingRoom Model 代表一個投票房間。
    使用 UUID 字串作為主鍵與專屬網址的一部分。
    """
    __tablename__ = 'voting_rooms'

    id = db.Column(db.String(36), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default='active', nullable=False)  # 'active' 或 'closed'

    # 關聯：一個房間可以有多個候選餐廳，房間刪除時其下的候選人也一併刪除
    candidates = db.relationship('RoomCandidate', backref='room', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<VotingRoom {self.id} (Status: {self.status})>"

    # ==========================================
    # CRUD Operations
    # ==========================================

    @classmethod
    def create(cls, id=None, status='active'):
        """
        新增投票房間。
        
        :param id: 房間 UUID/代碼 (選填，若無則自動產生前 8 碼)
        :param status: 房間狀態，預設為 'active'
        :return: 新增的 VotingRoom 物件
        """
        try:
            if not id:
                id = str(uuid.uuid4())[:8]
            
            room = cls(
                id=id,
                status=status
            )
            db.session.add(room)
            db.session.commit()
            return room
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def create_room(cls):
        """
        產生一個隨機的房間 ID 並寫入資料庫 (前 8 碼簡短代碼)。
        
        :return: 房間 ID (str)
        """
        room = cls.create()
        return room.id

    @classmethod
    def get_by_id(cls, id):
        """
        根據 ID (UUID) 取得單筆投票房間。
        
        :param id: 房間 UUID
        :return: VotingRoom 物件，若不存在則回傳 None
        """
        try:
            return cls.query.get(id)
        except Exception as e:
            raise e

    @classmethod
    def get_all(cls):
        """
        取得所有投票房間，依建立時間降序。
        
        :return: list[VotingRoom]
        """
        try:
            return cls.query.order_by(cls.created_at.desc()).all()
        except Exception as e:
            raise e

    @classmethod
    def update(cls, id, **kwargs):
        """
        更新投票房間資訊。
        
        :param id: 房間 UUID
        :param kwargs: 動態修改欄位與其對應值 (例如 status='closed')
        :return: 更新後的 VotingRoom 物件，若不存在則回傳 None
        """
        try:
            room = cls.query.get(id)
            if room:
                for key, value in kwargs.items():
                    if hasattr(room, key):
                        setattr(room, key, value)
                db.session.commit()
                return room
            return None
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def delete(cls, id):
        """
        刪除指定 ID 的投票房間。
        
        :param id: 房間 UUID
        :return: bool, 刪除成功回傳 True，若不存在則回傳 False
        """
        try:
            room = cls.query.get(id)
            if room:
                db.session.delete(room)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
