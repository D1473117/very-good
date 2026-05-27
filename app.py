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
            print(f"✅ Successfully initialized the database at {db_path} with schema.sql")

# 直接在此呼叫，確保 flask run 也能順利建表
init_db()

if __name__ == '__main__':
    # 執行伺服器
    app.run(debug=True, port=5000)
