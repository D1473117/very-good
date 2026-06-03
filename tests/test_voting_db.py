import sys
import os
import unittest

# 將專案路徑加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from app.models.voting_room import VotingRoom
from app.models.room_candidate import RoomCandidate
from app.models.restaurant import Restaurant

class TestVotingDatabase(unittest.TestCase):
    def setUp(self):
        # 建立測試用 App 並配置記憶體資料庫
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 建立所有資料表
        db.create_all()
        
        # 建立測試餐廳
        self.test_restaurant = Restaurant(
            name="測試餐廳",
            category="測試類別",
            price_range="$50-$150",
            rating=4.5,
            address="測試地址"
        )
        db.session.add(self.test_restaurant)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_voting_room_crud(self):
        # 1. Create Room
        room = VotingRoom.create(id="test-room-uuid")
        self.assertIsNotNone(room)
        self.assertEqual(room.id, "test-room-uuid")
        self.assertEqual(room.status, "active")
        
        # 2. Get Room by ID
        fetched_room = VotingRoom.get_by_id("test-room-uuid")
        self.assertIsNotNone(fetched_room)
        self.assertEqual(fetched_room.id, "test-room-uuid")
        
        # 3. Update Room
        updated_room = VotingRoom.update("test-room-uuid", status="closed")
        self.assertEqual(updated_room.status, "closed")
        
        # 4. Get All Rooms
        rooms = VotingRoom.get_all()
        self.assertEqual(len(rooms), 1)
        
        # 5. Delete Room
        deleted = VotingRoom.delete("test-room-uuid")
        self.assertTrue(deleted)
        self.assertIsNone(VotingRoom.get_by_id("test-room-uuid"))

    def test_room_candidate_crud(self):
        # 1. Create Room & Candidate
        room = VotingRoom.create(id="test-room-uuid")
        candidate = RoomCandidate.create(
            room_id=room.id,
            restaurant_id=self.test_restaurant.id,
            vote_count=0
        )
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.room_id, "test-room-uuid")
        self.assertEqual(candidate.restaurant_id, self.test_restaurant.id)
        self.assertEqual(candidate.vote_count, 0)
        
        # 2. Get Candidate by ID
        fetched_candidate = RoomCandidate.get_by_id(candidate.id)
        self.assertIsNotNone(fetched_candidate)
        self.assertEqual(fetched_candidate.restaurant.name, "測試餐廳")
        
        # 3. Get candidates by Room ID
        candidates = RoomCandidate.get_by_room_id("test-room-uuid")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].id, candidate.id)
        
        # 4. Increment Vote
        updated_candidate = RoomCandidate.increment_vote(candidate.id)
        self.assertEqual(updated_candidate.vote_count, 1)
        
        # 5. Update Candidate
        updated_candidate = RoomCandidate.update(candidate.id, vote_count=5)
        self.assertEqual(updated_candidate.vote_count, 5)
        
        # 6. Delete Candidate
        deleted = RoomCandidate.delete(candidate.id)
        self.assertTrue(deleted)
        self.assertIsNone(RoomCandidate.get_by_id(candidate.id))

    def test_cascade_delete(self):
        # 測試級聯刪除：刪除房間時，候選餐廳也應該一併被刪除
        room = VotingRoom.create(id="test-room-uuid")
        candidate = RoomCandidate.create(
            room_id=room.id,
            restaurant_id=self.test_restaurant.id,
            vote_count=0
        )
        
        # 確保候選餐廳確實存在
        self.assertIsNotNone(RoomCandidate.get_by_id(candidate.id))
        
        # 刪除房間
        VotingRoom.delete(room.id)
        
        # 確保房間和候選餐廳都已被刪除
        self.assertIsNone(VotingRoom.get_by_id(room.id))
        self.assertIsNone(RoomCandidate.get_by_id(candidate.id))

    def test_user_requested_methods(self):
        # 1. 測試 create_room (產生 8 碼隨機 ID)
        room_id = VotingRoom.create_room()
        self.assertEqual(len(room_id), 8)
        
        # 2. 測試 add_candidate
        candidate = RoomCandidate.add_candidate(room_id, self.test_restaurant.id)
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.room_id, room_id)
        self.assertEqual(candidate.restaurant_id, self.test_restaurant.id)
        self.assertEqual(candidate.vote_count, 0)
        
        # 3. 測試 vote
        updated_candidate = RoomCandidate.vote(room_id, self.test_restaurant.id)
        self.assertIsNotNone(updated_candidate)
        self.assertEqual(updated_candidate.vote_count, 1)

if __name__ == '__main__':
    unittest.main()

