DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS recommendation_history;

CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    rating REAL,
    budget_level INTEGER DEFAULT 1, -- 1: 平價, 2: 中等, 3: 昂貴
    google_maps_url TEXT
);

CREATE TABLE recommendation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    restaurant_name TEXT NOT NULL,
    place_id TEXT,
    lat REAL,
    lng REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
