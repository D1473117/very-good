-- ==========================================
-- 隨便吃什麼都好 — SQLite 建表語法
-- 檔案路徑：database/schema.sql
-- 說明：本系統透過 Flask-SQLAlchemy db.create_all()
--       自動建立資料表，此檔案僅作為參考文件。
--       若需手動重建，可執行：
--       sqlite3 instance/database.db < database/schema.sql
-- ==========================================

-- 使用者帳號
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(120) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 餐廳資料
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(50) NOT NULL,
    rating FLOAT NOT NULL DEFAULT 0.0,
    address VARCHAR(255) NOT NULL,
    price_level INTEGER NOT NULL,   -- 1: 平價($)  2: 中等($$)  3: 昂貴($$$)  4: 奢華($$$$)
    distance INTEGER NOT NULL,      -- 單位：公尺
    lat FLOAT,
    lng FLOAT
);

-- 會員收藏（User 與 Restaurant 的多對多關聯表）
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 餐廳評論與評分
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    rating FLOAT NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 隨機抽選歷史紀錄（僅在使用者已登入時記錄）
CREATE TABLE IF NOT EXISTS spin_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    distance INTEGER,               -- 當時設定的搜尋半徑（公尺）
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 使用者個人偏好設定（支援登入會員與未登入訪客）
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),        -- 未登入訪客的 Session ID
    default_radius INTEGER NOT NULL DEFAULT 3000,
    default_min_price INTEGER NOT NULL DEFAULT 1,
    default_max_price INTEGER NOT NULL DEFAULT 3,
    favorite_cuisines TEXT NOT NULL DEFAULT '[]'    -- JSON 陣列字串，如 ["日式","台式"]
);

-- 多人投票房間（PK 使用短碼 UUID 字串，方便作為可分享的 URL）
CREATE TABLE IF NOT EXISTS vote_rooms (
    id VARCHAR(36) PRIMARY KEY,     -- 取 UUID v4 前 8 碼，如 "a3f9bc12"
    title VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 投票房間選項（每個房間包含多個候選餐廳）
CREATE TABLE IF NOT EXISTS vote_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id VARCHAR(36) NOT NULL REFERENCES vote_rooms(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    votes INTEGER NOT NULL DEFAULT 0    -- 目前得票數
);
