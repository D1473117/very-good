# 系統與使用者流程圖設計說明書 (FLOWCHART.md)

本文件依據 [產品需求文件 (PRD.md)](file:///c:/Users/AmyLin/OneDrive/桌面/very-good-1/docs/PRD.md) 與 [系統架構設計說明書 (ARCHITECTURE.md)](file:///c:/Users/AmyLin/OneDrive/桌面/very-good-1/docs/ARCHITECTURE.md) 的規格，規劃並視覺化「隨機推薦系統 - 隨便吃什麼都好」的**使用者操作流程 (User Flow)**、**系統非同步交互序列圖 (Sequence Diagram)**，以及**系統功能路由對照表**。

---

## 1. 使用者流程圖 (User Flow)

此流程圖描述使用者從進入系統首頁開始，進行免登入抽取、帳號註冊登入、我的最愛管理、評論寫入與刪除、專屬最愛抽取，以及 GPS 定位引導的完整操作路徑。

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B[首頁 - 歡迎畫面]
    
    %% 訪客路徑
    B --> C{是否登入？}
    C -->|訪客狀態| D[點擊「隨便抽一家」]
    D --> E[AJAX 發送推薦請求 /api/random]
    E --> F[顯示餐廳推薦卡片]
    
    F --> F1[一鍵點擊「導航去吃」] --> F2([開啟 Google Maps 外鏈])
    F --> F3[點擊「再抽一次」] --> D
    F --> F4{點擊「加入最愛」或「寫評論」}
    F4 -->|未登入限制| F5[瀏覽器 Alert 提示] --> G[引導至 登入/註冊 頁面]
    
    %% 註冊登入路徑
    C -->|前往認證| G
    G --> G1[註冊帳號 /register] --> G2[註冊成功並自動登入] --> H[已登入狀態 - 首頁]
    G --> G3[登入帳號 /login] --> G4[登入成功] --> H
    
    %% 已登入首頁互動路徑
    H --> I[展開「進階篩選面板」]
    I --> I1[選擇：餐點類型 / 預算價格 / 最低評分] --> J[點擊「隨便抽一家」]
    J --> K[AJAX 帶篩選參數請求 /api/random]
    K --> L[渲染 Premium 卡片]
    
    %% Premium 資訊展示與互動
    L --> L1[GPS 自動運算距離與步行/騎車時間]
    L --> L2[即時分析營業時間顯示 營業中/即將打烊 呼吸燈]
    L --> L3[渲染招牌菜 Pill 標籤與美元量規]
    
    L --> L4[點擊「愛心 ❤️ 收藏」] --> L5[AJAX 切換收藏狀態] --> L6([即時更新愛心實心/空心狀態])
    L --> L7[撰寫評論並選擇 1~5 星] --> L8[AJAX 送出 /api/reviews/add] --> L9([評論區即時無刷新渲染呈現])
    
    %% 最愛專頁與評論專頁路徑
    H --> M[點擊 Navbar「我的收藏」/favorites]
    M --> M1[瀏覽收藏餐廳網格]
    M1 --> M2[點擊卡片「取消收藏」] --> M3[AJAX 請求且卡片優雅淡出移除]
    M1 --> M4[點擊「從最愛抽一家」金色骰子] --> M5[AJAX 請求 /api/favorites/draw] --> M6([彈出金色皇冠推薦卡片])
    
    H --> N[點擊 Navbar「評論紀錄」/reviews]
    N --> N1[瀏覽個人評論歷史時間軸 Timeline]
    N1 --> N2[點擊「刪除評論」] --> N3[AJAX 刪除且該評論卡片淡出移除]
    
    H --> O[點擊「登出」/logout] --> P([清除 Session 並重定向回訪客首頁])
```

---

## 2. 系統序列圖 (Sequence Diagram)

為優化使用者體驗，系統大量採用混合式渲染（Hybrid Rendering），小互動均以非同步 AJAX (Fetch API) 進行。以下詳細呈現兩個核心流程的底層互動順序。

### 2.1 登入用戶新增評論與即時渲染流程 (AJAX Add Review Flow)

此流程描述已登入使用者在推薦卡片下方撰寫評論、評分，並點擊送出時，資料如何在瀏覽器、Flask 後端與 SQLite 資料庫之間流動，並完成無刷新前端更新。

```mermaid
sequenceDiagram
    autonumber
    actor User as 已登入使用者
    participant Browser as 瀏覽器前端 (main.js)
    participant Flask as Flask Route (routes.py)
    participant Model as Database Model (models.py)
    participant DB as SQLite 資料庫
    
    User->>Browser: 點選星等 (1~5) 並輸入評論文字，點擊「發表評語」
    Note over Browser: 檢查 restaurant_id 與 rating 是否選取
    Browser->>Flask: POST /api/reviews/add (JSON: {restaurant_id, rating, comment})
    Note over Flask: 檢查 Session 中是否含有 user_id
    alt 未登入 (Session 無 user_id)
        Flask-->>Browser: 回傳 401 Unauthorized (JSON 錯誤訊息)
        Browser->>User: 提示登入，並導向 /login 頁面
    else 已登入
        Flask->>Model: add_review(user_id, restaurant_id, rating, comment)
        Model->>DB: INSERT INTO Review (user_id, restaurant_id, rating, comment)...
        DB-->>Model: 寫入成功
        Note over Flask: 為使前端立即呈現最新數據，重新查詢該餐廳評論清單
        Flask->>Model: get_restaurant_reviews(restaurant_id)
        Model->>DB: SELECT rv.*, u.username FROM Review JOIN User... WHERE restaurant_id = ?
        DB-->>Model: 回傳最新評論紀錄列表 (dict rows)
        Model-->>Flask: 回傳評論 Python List
        Flask-->>Browser: 回傳 200 OK JSON: {"status": "success", "message": "...", "reviews": [...]}
        Note over Browser: 執行 renderReviews(reviews)
        Note over Browser: 遍歷 reviews 陣列，生成 HTML 並更新 DOM (#restaurant-reviews-list)
        Browser-->>User: 畫面無刷新，立即於評論列表頂端看到自己發表的評語！
    end
```

---

### 2.2 條件篩選隨機推薦與 GPS/時間運算流程 (AJAX Recommendation & Premium Display)

此流程描述使用者設定篩選條件點擊抽取後，系統透過 API 獲取隨機餐廳，並由前端 JS 結合 GPS 計算精準距離與動態營業狀態的完整互動。

```mermaid
sequenceDiagram
    autonumber
    actor User as 使用者
    participant Browser as 瀏覽器前端 (main.js)
    participant Flask as Flask Route (routes.py)
    participant Model as Database Model (models.py)
    participant DB as SQLite 資料庫

    User->>Browser: 展開進階篩選，設定餐點類型/價格/評分，點擊「隨便抽一家」
    Note over Browser: 啟動抽取動畫效果，按鈕轉為 Loading 狀態
    
    rect rgb(240, 248, 255)
        Note over Browser: [定位引擎處理]
        opt 瀏覽器支援 Geolocation
            Browser->>Browser: 呼叫 navigator.geolocation.getCurrentPosition
            alt 使用者允許定位
                Browser->>Browser: 取得真實 GPS 經緯度座標 (userLocation)
            else 使用者拒絕定位
                Browser->>Browser: 使用台北 101 座標 (25.033964, 121.564468) 作為 Fallback
            end
        end
    end

    Browser->>Flask: GET /api/random?category=X&price_level=Y&min_rating=Z
    Note over Flask: 從 Session 讀取 user_id (若有，用於判斷是否已加入最愛)
    Flask->>Model: get_random_restaurant(category, price_level, min_rating, user_id)
    Model->>DB: SELECT * FROM Restaurant WHERE category = ? AND price_level = ? AND rating >= ?
    DB-->>Model: 回傳符合條件的餐廳資料清單
    Note over Model: 執行隨機演算法隨機挑選一家餐廳
    opt 已登入狀態
        Model->>Model: 查詢 Favorite 表確認是否被此 user_id 收藏
    end
    Model-->>Flask: 回傳選中的餐廳資料 dict
    Flask->>Model: get_restaurant_reviews(restaurant_id)
    Model->>DB: 查詢該餐廳之歷史評價
    DB-->>Model: 回傳評價列表
    Flask-->>Browser: 回傳 200 OK JSON: {"status": "success", "data": {...}, "reviews": [...]}
    
    rect rgb(255, 245, 238)
        Note over Browser: [Premium 視覺運算渲染]
        Browser->>Browser: 1. 執行 Haversine 公式計算 GPS 與餐廳經緯度之實際距離
        Browser->>Browser: 2. 依據距離計算步行時間（5km/h）與騎車時間（30km/h）
        Browser->>Browser: 3. 解析營業時段（支援跨夜，如11:00-04:00），比對目前時間運算動態營業狀態呼吸徽章
        Browser->>Browser: 4. 渲染招牌 Pill 標籤、價格量規與饕客評論
    end
    
    Browser-->>User: 呈現高質感 RWD 卡片，包含呼吸 badge、估算分鐘數、招牌菜與評價！
```

---

## 3. 功能清單與路由對照表 (Routing Table)

以下為本專案完整的 Controller 路由清單，包含前端視圖渲染路由與非同步 AJAX API 端點對照。

| 功能名稱 | 路由路徑 (URL) | HTTP 方法 | 回傳格式 | 參數說明 | 權限要求 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **首頁** | `/` | `GET` | HTML (Jinja2) | 無 | 訪客 / 會員 |
| **會員註冊** | `/register` | `GET`, `POST` | HTML / Redirect | `POST` 表單: `username`, `password`, `confirm_password` | 訪客 |
| **會員登入** | `/login` | `GET`, `POST` | HTML / Redirect | `POST` 表單: `username`, `password` | 訪客 |
| **會員登出** | `/logout` | `GET` | Redirect | 無 | 會員 |
| **進階篩選隨機推薦 API** | `/api/random` | `GET` | JSON | Query 參數 (選填): `category`, `price_level`, `min_rating` | 訪客 / 會員 |
| **我的最愛專頁** | `/favorites` | `GET` | HTML (Jinja2) | 無 | 會員 (未登入重導向) |
| **切換最愛收藏 API** | `/api/favorites/toggle` | `POST` | JSON | `POST` JSON: `restaurant_id` | 會員 (未登入 401) |
| **最愛限定抽取 API** | `/api/favorites/draw` | `GET` | JSON | 無 | 會員 (未登入 401) |
| **我的評價專頁** | `/reviews` | `GET` | HTML (Jinja2) | 無 | 會員 (未登入重導向) |
| **發布評論 API** | `/api/reviews/add` | `POST` | JSON | `POST` JSON: `restaurant_id`, `rating` (1-5), `comment` | 會員 (未登入 401) |
| **刪除評論 API** | `/api/reviews/delete/<review_id>` | `POST`, `DELETE` | JSON | 路由參數: `review_id` | 會員 (未登入 401 / 限作者) |

---

## 4. 關鍵流程節點說明 (UX Touchpoints)

1. **認證邊界處理**：
   - 訪客可以無障礙使用「首頁隨便抽一家」與「進階篩選」。
   - 當訪客意圖點擊推薦結果卡片左上角的「愛心」進行收藏，或意圖在卡片下方填寫評論時，系統會以精美的前端 Alert 提示，並引導至登入畫面，保留原操作意圖。
2. **無刷新（AJAX）交互**：
   - 點擊「愛心」收藏時，愛心瞬間變紅並產生放大動畫，後端靜默更新資料庫。
   - 在「我的收藏」或「我的評價」點擊移除/刪除時，前端會彈出確認視窗，確認後該卡片會套用 `.fade-out` CSS 動畫淡出，並在 400ms 後從 DOM 移除，其餘卡片自動流暢重排，避免傳統整頁刷新帶來的卡頓感。
3. **定位權限失敗容錯**：
   - 定位模組在載入首頁時即於背景非同步請求權限。若使用者點選「拒絕」，系統將座標無縫設定在「台北 101」，並顯示「示範距離」灰色微章，此設計既不影響核心推薦功能，又能在視覺上維持精美的欄位排版。
