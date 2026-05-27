-- ==========================================
-- F-05 收藏與歷史紀錄模組建表語法 (SQLite)
-- 專案：隨便吃什麼都好（Let's Just Eat）
-- ==========================================

-- 1. 建立收藏資料表
CREATE TABLE IF NOT EXISTS favorites (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    restaurant_name VARCHAR(100) NOT NULL,
    category    VARCHAR(50),
    rating      FLOAT        CHECK(rating >= 1.0 AND rating <= 5.0),
    address     VARCHAR(200),
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. 建立歷史推薦紀錄資料表
CREATE TABLE IF NOT EXISTS history (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    restaurant_name VARCHAR(100) NOT NULL,
    category    VARCHAR(50),
    rating      FLOAT        CHECK(rating >= 1.0 AND rating <= 5.0),
    recommended_at DATETIME  DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. 建立索引優化查詢效能
-- 依收藏時間降序查詢（個人收藏清單頁面常用）
CREATE INDEX IF NOT EXISTS idx_favorites_created_at
    ON favorites(created_at DESC);

-- 依推薦時間降序查詢（歷史紀錄列表頁面常用）
CREATE INDEX IF NOT EXISTS idx_history_recommended_at
    ON history(recommended_at DESC);
