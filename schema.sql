DROP TABLE IF EXISTS restaurants;

CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    price_level INTEGER NOT NULL,
    distance INTEGER NOT NULL,
    address TEXT NOT NULL,
    rating REAL NOT NULL
);

INSERT INTO restaurants (name, type, price_level, distance, address, rating) VALUES
('一蘭拉麵 台中朝富店', '日式', 2, 800, '台中市西屯區朝富路2號', 4.5),
('屋馬燒肉 中港店', '日式', 3, 1500, '台中市西屯區台灣大道三段300號', 4.8),
('輕井澤鍋物 公益店', '火鍋', 2, 2500, '台中市西區公益路276號', 4.4),
('宮原眼科', '甜點', 2, 4000, '台中市中區中山路20號', 4.3),
('麥當勞 台中逢甲店', '速食', 1, 500, '台中市西屯區福星路427號', 4.0),
('星巴克 國家歌劇院門市', '咖啡廳', 2, 1200, '台中市西屯區惠來路二段101號', 4.6),
('春水堂 創始店', '台式', 2, 3500, '台中市西區四維街30號', 4.2),
('俺達の肉屋', '日式', 4, 2000, '台中市西區公益路192-1號', 4.9),
('茶六燒肉堂 朝富店', '日式', 3, 900, '台中市西屯區朝富路258號', 4.7),
('刁民酸菜魚 逢甲店', '台式', 2, 600, '台中市西屯區福星路591號', 4.5);
