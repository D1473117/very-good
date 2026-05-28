DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS recommendation_history;
DROP TABLE IF EXISTS favorites;

-- 1. 餐廳資料表
CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    rating REAL,
    budget_level INTEGER DEFAULT 1, -- 1: 平價, 2: 中等, 3: 昂貴
    google_maps_url TEXT,
    is_custom INTEGER DEFAULT 0,    -- 0: 系統預設, 1: 使用者自訂
    session_id TEXT                 -- 關聯建立者的 session_id，避免他人看見自訂餐廳
);

-- 2. 推薦歷史與評論日誌表
CREATE TABLE recommendation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    restaurant_id INTEGER,
    restaurant_name TEXT NOT NULL,
    place_id TEXT,
    lat REAL,
    lng REAL,
    user_rating INTEGER,            -- 使用者給出的星星 (1-5)
    comment TEXT,                   -- 使用者的評論內容
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(restaurant_id) REFERENCES restaurants(id) ON DELETE SET NULL
);

-- 3. 會員收藏 (口袋名單) 表
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    restaurant_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    UNIQUE(session_id, restaurant_id)
);


