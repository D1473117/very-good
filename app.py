"""
app.py

Flask 專案的啟動入口點。
負責實例化應用程式，確保 SQLite 資料表建立，並在本地運行 Flask 開發伺服器。
"""
from app import create_app
from app.models import db

# 透過 App Factory 建立 Flask 實例
app = create_app()

# 確保 SQLite 資料庫表存在於 instance/database.db 中
# 如果資料表尚未建立，SQLAlchemy 會自動根據 Model 結構建立它們，且不會影響現有資料。
with app.app_context():
    try:
        db.create_all()
        print("[SQLite] 資料庫連線初始化成功！資料表 favorites、history 已就緒。")
    except Exception as e:
        print(f"[SQLite] 資料庫初始化失敗，錯誤原因：{e}")

if __name__ == '__main__':
    # 啟動本地開發伺服器
    # 預設執行於 http://127.0.0.1:5000
    app.run(host='127.0.0.1', port=5000, debug=True)
