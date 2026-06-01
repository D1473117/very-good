import os
import sqlite3
from app import create_app
from app.models import db

app = create_app()

def init_db():
    """初始化 SQLite 資料庫與 schema，無論是 python app.py 或 flask run 都會被執行"""
    with app.app_context():
        # 確保 instance 資料夾存在
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, 'database.db')
        
        # 判斷如果資料庫檔案不存在或為空，則執行 schema.sql
        if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
            schema_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'schema.sql')
            
            with sqlite3.connect(db_path) as conn:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
            print(f"[SUCCESS] Successfully initialized the database at {db_path} with schema.sql")

        # 使用 SQLAlchemy 確保所有資料表都已建立 (包含後來新增的 restaurants 欄位表)
        db.create_all()

        # 匯入餐廳種子資料
        from app.models.restaurant import Restaurant
        try:
            if Restaurant.query.first() is None:
                import json
                seed_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'restaurants_seed.json')
                if os.path.exists(seed_path):
                    with open(seed_path, 'r', encoding='utf-8') as f:
                        restaurants_data = json.load(f)
                        for item in restaurants_data:
                            r = Restaurant(
                                name=item['name'],
                                category=item.get('category'),
                                price_range=item.get('price_range'),
                                rating=item.get('rating'),
                                address=item.get('address'),
                                phone=item.get('phone'),
                                operating_hours=item.get('operating_hours'),
                                image_url=item.get('image_url'),
                                google_maps_url=item.get('google_maps_url'),
                                latitude=item.get('latitude'),
                                longitude=item.get('longitude')
                            )
                            db.session.add(r)
                    db.session.commit()
                    print(f"[SUCCESS] Successfully seeded {len(restaurants_data)} restaurants into the database.")
        except Exception as e:
            db.session.rollback()
            print(f"[WARNING] Error seeding database: {str(e)}")



# 直接在此呼叫，確保 flask run 也能順利建表
init_db()

if __name__ == '__main__':
    # 執行伺服器
    app.run(debug=True, port=5000)
