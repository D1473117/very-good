import sys
import os
import unittest
import json

# 將專案路徑加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from app.models.voting_room import VotingRoom
from app.models.room_candidate import RoomCandidate
from app.models.restaurant import Restaurant

class TestVotingRoutes(unittest.TestCase):
    def setUp(self):
        # 建立測試用 App 並配置記憶體資料庫
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 建立所有資料表
        db.create_all()
        
        # 建立兩個測試餐廳
        self.restaurant1 = Restaurant(name="餐廳一", category="日式")
        self.restaurant2 = Restaurant(name="餐廳二", category="義式")
        db.session.add_all([self.restaurant1, self.restaurant2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_room_success(self):
        # 測試成功建立房間 (JSON 格式)
        response = self.client.post('/voting/create', json={
            'restaurant_ids': [self.restaurant1.id, self.restaurant2.id]
        })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('room_id', data)
        self.assertIn('room_url', data)
        
        # 驗證資料庫中是否確實寫入
        room = VotingRoom.get_by_id(data['room_id'])
        self.assertIsNotNone(room)
        candidates = RoomCandidate.get_by_room_id(data['room_id'])
        self.assertEqual(len(candidates), 2)

    def test_create_room_form_success(self):
        # 測試成功建立房間 (Form 格式)
        response = self.client.post('/voting/create', data={
            'restaurant_ids': [self.restaurant1.id, self.restaurant2.id]
        })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        
        # 驗證資料庫中是否確實寫入
        room = VotingRoom.get_by_id(data['room_id'])
        self.assertIsNotNone(room)

    def test_create_room_invalid_input(self):
        # 測試餐廳數量不足 2 家時
        response = self.client.post('/voting/create', json={
            'restaurant_ids': [self.restaurant1.id]
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')

    def test_get_room_page(self):
        # 建立房間與候選餐廳
        room_id = VotingRoom.create_room()
        RoomCandidate.add_candidate(room_id, self.restaurant1.id)
        RoomCandidate.add_candidate(room_id, self.restaurant2.id)
        
        # 測試載入投票頁面（GET）
        response = self.client.get(f'/voting/{room_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("決戰時刻", response.data.decode('utf-8'))
        self.assertIn(room_id, response.data.decode('utf-8'))

    def test_get_room_page_not_found(self):
        # 測試載入不存在的投票頁面
        response = self.client.get('/voting/invalid-room-id')
        self.assertEqual(response.status_code, 404)

    def test_vote_success(self):
        # 建立房間與候選餐廳
        room_id = VotingRoom.create_room()
        RoomCandidate.add_candidate(room_id, self.restaurant1.id)
        
        response = self.client.post(f'/voting/{room_id}/vote', json={
            'restaurant_id': self.restaurant1.id
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        
        # 驗證票數增加
        candidates = RoomCandidate.get_by_room_id(room_id)
        self.assertEqual(candidates[0].vote_count, 1)

    def test_results_success(self):
        room_id = VotingRoom.create_room()
        RoomCandidate.add_candidate(room_id, self.restaurant1.id)
        RoomCandidate.vote(room_id, self.restaurant1.id)
        
        response = self.client.get(f'/voting/{room_id}/results')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['results'][0]['restaurant_id'], self.restaurant1.id)
        self.assertEqual(data['results'][0]['vote_count'], 1)

if __name__ == '__main__':
    unittest.main()
