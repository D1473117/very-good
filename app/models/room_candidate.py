from app.models import db

class RoomCandidate(db.Model):
    """
    RoomCandidate Model 代表投票房間內的候選餐廳。
    """
    __tablename__ = 'room_candidates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.String(36), db.ForeignKey('voting_rooms.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    vote_count = db.Column(db.Integer, default=0, nullable=False)

    # 關聯：候選餐廳對應之餐廳詳細資訊
    restaurant = db.relationship('Restaurant', backref='room_candidates', lazy=True)

    def __repr__(self):
        return f"<RoomCandidate ID: {self.id} (Room: {self.room_id}, Restaurant: {self.restaurant_id}, Votes: {self.vote_count})>"

    # ==========================================
    # CRUD Operations
    # ==========================================

    @classmethod
    def create(cls, room_id, restaurant_id, vote_count=0):
        """
        新增房間的候選餐廳。
        
        :param room_id: 關聯的房間 UUID
        :param restaurant_id: 關聯的餐廳 ID
        :param vote_count: 初始得票數，預設為 0
        :return: 新增的 RoomCandidate 物件
        """
        try:
            candidate = cls(
                room_id=room_id,
                restaurant_id=restaurant_id,
                vote_count=vote_count
            )
            db.session.add(candidate)
            db.session.commit()
            return candidate
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def add_candidate(cls, room_id, restaurant_id):
        """
        將候選餐廳加入該投票房間。
        
        :param room_id: 房間 ID
        :param restaurant_id: 餐廳 ID
        :return: 新增的 RoomCandidate 物件
        """
        return cls.create(room_id=room_id, restaurant_id=restaurant_id)

    @classmethod
    def vote(cls, room_id, restaurant_id):
        """
        為特定房間的特定餐廳投下一票。
        
        :param room_id: 房間 ID
        :param restaurant_id: 餐廳 ID
        :return: 更新後的 RoomCandidate 物件，若不存在則回傳 None
        """
        try:
            candidate = cls.query.filter_by(room_id=room_id, restaurant_id=restaurant_id).first()
            if candidate:
                candidate.vote_count += 1
                db.session.commit()
                return candidate
            return None
        except Exception as e:
            db.session.rollback()
            raise e


    @classmethod
    def get_by_id(cls, id):
        """
        根據 ID 取得單筆房間候選餐廳資訊。
        
        :param id: 候選 ID
        :return: RoomCandidate 物件，若不存在則回傳 None
        """
        try:
            return cls.query.get(id)
        except Exception as e:
            raise e

    @classmethod
    def get_by_room_id(cls, room_id):
        """
        根據 Room ID 取得該房間所有的候選餐廳，依得票數降序。
        
        :param room_id: 房間 UUID
        :return: list[RoomCandidate]
        """
        try:
            return cls.query.filter_by(room_id=room_id).order_by(cls.vote_count.desc()).all()
        except Exception as e:
            raise e

    @classmethod
    def get_all(cls):
        """
        取得所有房間的候選餐廳。
        
        :return: list[RoomCandidate]
        """
        try:
            return cls.query.all()
        except Exception as e:
            raise e

    @classmethod
    def increment_vote(cls, id):
        """
        將特定候選餐廳的票數加 1。
        
        :param id: 候選 ID
        :return: 更新後的 RoomCandidate 物件，若不存在則回傳 None
        """
        try:
            candidate = cls.query.get(id)
            if candidate:
                candidate.vote_count += 1
                db.session.commit()
                return candidate
            return None
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def update(cls, id, **kwargs):
        """
        更新候選餐廳欄位資訊。
        
        :param id: 候選 ID
        :param kwargs: 動態修改欄位與其對應值 (例如 vote_count=5)
        :return: 更新後的 RoomCandidate 物件，若不存在則回傳 None
        """
        try:
            candidate = cls.query.get(id)
            if candidate:
                for key, value in kwargs.items():
                    if hasattr(candidate, key):
                        setattr(candidate, key, value)
                db.session.commit()
                return candidate
            return None
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def delete(cls, id):
        """
        刪除指定的房間候選餐廳。
        
        :param id: 候選 ID
        :return: bool, 刪除成功回傳 True，若不存在則回傳 False
        """
        try:
            candidate = cls.query.get(id)
            if candidate:
                db.session.delete(candidate)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
