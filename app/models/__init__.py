"""
app/models/__init__.py

Flask-SQLAlchemy 共用 db 實例初始化。

使用方式：
    from app.models import db

在 create_app() 工廠函數中呼叫：
    db.init_app(app)

資料庫檔案路徑（SQLite）：
    instance/database.db
"""
from flask_sqlalchemy import SQLAlchemy

# 建立共用 SQLAlchemy 實例，供所有 Model 匯入使用
db = SQLAlchemy()

__all__ = ['db']
