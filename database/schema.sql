-- SQLite 資料庫 Schema 定義檔案 (schema.sql)

-- 1. 餐廳資料表 (Restaurant)
-- 用於儲存餐廳的基本資訊，包括名稱、評分、營業時間、經緯度座標以及 Premium 加分欄位 (價格區間、餐點類型、招牌美味)
CREATE TABLE IF NOT EXISTS Restaurant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 餐廳主鍵
    place_id TEXT,                                -- Google Places API 唯一識別 ID (快取用)
    name TEXT NOT NULL,                           -- 餐廳名稱 (必填)
    address TEXT,                                 -- 完整地址
    rating REAL,                                  -- 平均星級評分 (0.0 - 5.0)
    user_ratings_total INTEGER,                   -- 總評分人數
    open_hours TEXT,                              -- 營業時間字串 (如 "11:00 - 21:00" 或 "24 小時營業")
    photo_url TEXT,                               -- 餐廳美食封面照網址
    latitude REAL,                                -- 緯度座標 (GPS Haversine 運算用)
    longitude REAL,                               -- 經度座標 (GPS Haversine 運算用)
    price_level INTEGER,                          -- 價格等級量規 (1: 平價, 2: 中等, 3: 高檔, 4: 奢華)
    category TEXT,                                -- 餐點類型 (如 "日式", "火鍋", "速食")
    signature TEXT                                -- 👑 招牌必點推薦菜色 (如 "招牌小籠包、排骨蛋炒飯")
);

-- 2. 會員帳號資料表 (User)
-- 用於儲存用戶的登入認證資訊，密碼採用安全雜湊 (Password Hash) 加密儲存
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 會員主鍵
    username TEXT UNIQUE NOT NULL,                -- 唯一使用者帳號 (必填，唯一約束)
    password_hash TEXT NOT NULL,                  -- PBKDF2 安全加密之密碼雜湊值 (必填)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 帳號註冊時間
);

-- 3. 我的最愛收藏關聯表 (Favorite)
-- 建立 User 與 Restaurant 之間的多對多 (Many-to-Many) 關聯，紀錄用戶收藏的餐廳
CREATE TABLE IF NOT EXISTS Favorite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 收藏紀錄主鍵
    user_id INTEGER NOT NULL,                     -- 關聯會員 ID
    restaurant_id INTEGER NOT NULL,               -- 關聯餐廳 ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 收藏加入時間
    FOREIGN KEY (user_id) REFERENCES User (id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant (id) ON DELETE CASCADE,
    UNIQUE(user_id, restaurant_id)                 -- 複合唯一約束，防止重複收藏同家餐廳
);

-- 4. 饕客評價與評論資料表 (Review)
-- 建立 User 與 Restaurant 之間的一對多 (One-to-Many) 關聯，紀錄用戶對各餐廳的留言與評分
CREATE TABLE IF NOT EXISTS Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 評論紀錄主鍵
    user_id INTEGER NOT NULL,                     -- 關聯發言會員 ID
    restaurant_id INTEGER NOT NULL,               -- 關聯被評論餐廳 ID
    rating INTEGER NOT NULL,                      -- 用戶給予星等 (1 - 5 星)
    comment TEXT,                                 -- 用戶文字評語 (選填)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 評論發表時間
    FOREIGN KEY (user_id) REFERENCES User (id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant (id) ON DELETE CASCADE
);
