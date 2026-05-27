-- database/schema.sql
-- F-05 收藏與歷史紀錄模組建表語法 (SQLite)

-- 1. 建立收藏資料表
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_name TEXT NOT NULL,
    category TEXT,
    rating REAL,
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. 建立歷史推薦紀錄資料表
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_name TEXT NOT NULL,
    category TEXT,
    rating REAL,
    recommended_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. 建立索引優化查詢與過濾效能
CREATE INDEX IF NOT EXISTS idx_favorites_name ON favorites(restaurant_name);
CREATE INDEX IF NOT EXISTS idx_history_name ON history(restaurant_name);
