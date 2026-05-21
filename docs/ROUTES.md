# 系統路由與頁面設計說明書 (ROUTES.md)

本文件依據 [產品需求文件 (PRD.md)](file:///c:/Users/AmyLin/OneDrive/桌面/very-good-1/docs/PRD.md)、[系統架構設計說明書 (ARCHITECTURE.md)](file:///c:/Users/AmyLin/OneDrive/桌面/very-good-1/docs/ARCHITECTURE.md)、[流程圖設計說明書 (FLOWCHART.md)](file:///c:/Users/AmyLin/OneDrive/桌面/very-good-1/docs/FLOWCHART.md) 與 [資料庫設計說明書 (DB_DESIGN.md)](file:///c:/Users/AmyLin/OneDrive/桌面/very-good-1/docs/DB_DESIGN.md)，規劃並詳細記錄「隨機推薦系統 - 隨便吃什麼都好」的頁面路由與 API 端點設計。

---

## 1. 路由總覽表格 (Routing Overview)

本系統的頁面導覽採用伺服器端渲染 (SSR) 搭配 Jinja2 模板；最愛收藏、評價寫入與隨機抽取等頻繁小互動則規劃為非同步 AJAX API 端點。

| 功能名稱 | HTTP 方法 | URL 路由路徑 | 對應 Jinja2 模板檔案 | 說明描述 |
| :--- | :--- | :--- | :--- | :--- |
| **首頁入口** | `GET` | `/` | `app/templates/index.html` | 系統主要歡迎頁，包含隨機抽取卡片與進階篩選面板。 |
| **註冊頁面** | `GET` | `/register` | `app/templates/register.html`| 顯示高質感註冊表單。 |
| **註冊送出** | `POST` | `/register` | — (重導向回首頁) | 接收註冊欄位，寫入 DB 並自動登入。 |
| **登入頁面** | `GET` | `/login` | `app/templates/login.html` | 顯示登入表單。 |
| **登入送出** | `POST` | `/login` | — (重導向回首頁) | 驗證帳密，寫入 Session。 |
| **帳號登出** | `GET` | `/logout` | — (重導向回首頁) | 清除 Session 登入狀態。 |
| **條件推薦 API**| `GET` | `/api/random` | — (回傳 JSON 數據) | 依據餐點、價格、評分進行隨機推薦，並回傳評價。 |
| **最愛收藏專頁**| `GET` | `/favorites` | `app/templates/favorites.html`| 展示已收藏餐廳，提供「最愛抽一家」金色轉盤。 |
| **切換收藏 API**| `POST` | `/api/favorites/toggle`| — (回傳 JSON 數據) | 非同步新增或取消收藏。 |
| **最愛抽取 API**| `GET` | `/api/favorites/draw` | — (回傳 JSON 數據) | 限定在收藏清單中隨機抽取一家餐廳。 |
| **評價歷史專頁**| `GET` | `/reviews` | `app/templates/reviews.html` | 展示個人歷史發表之評論 TimeLine。 |
| **發布評論 API**| `POST` | `/api/reviews/add` | — (回傳 JSON 數據) | 用戶發布評語，寫入後即時回傳該店最新評價。 |
| **刪除評論 API**| `POST` / `DELETE` | `/api/reviews/delete/<id>`| — (回傳 JSON 數據) | 刪除指定評論，僅限該評論的撰寫者。 |

---

## 2. 路由詳細說明與邏輯處理 (Detailed Route Schemas)

### 2.1 餐廳條件推薦 API (`GET /api/random`)
* **輸入參數**：
  * `category` (Query): 餐點類型（如 "日式"、"火鍋"、"速食"、"all" 預設）。
  * `price_level` (Query): 價格等級（1-3，或 "all" 預設）。
  * `min_rating` (Query): 最低評分門檻（如 4.0、"all" 預設）。
* **處理邏輯**：
  1. 呼叫 `get_random_restaurant(category, price_level, min_rating, user_id)`。
  2. 若有登入（Session 存在 `user_id`），一併查詢該餐廳是否已為當前用戶所收藏。
  3. 呼叫 `get_restaurant_reviews(restaurant_id)` 獲取該餐廳的饕客評價。
* **輸出格式**：
  * **成功 (200 OK)**：
    ```json
    {
      "status": "success",
      "data": { "id": 1, "name": "麥當勞", "latitude": 25.03, "longitude": 121.56, "price_level": 1, "category": "速食", "signature": "大麥克" ... },
      "reviews": [...]
    }
    ```
  * **無匹配 (404 Not Found)**：`{"status": "error", "message": "找不到符合篩選條件的餐廳..."}`

---

### 2.2 切換最愛收藏 API (`POST /api/favorites/toggle`)
* **輸入參數**：
  * `restaurant_id` (JSON Payload): 欲收藏或取消收藏的餐廳 ID。
* **處理邏輯**：
  1. 檢查 Session 登入狀態，未登入回傳 401 錯誤。
  2. 呼叫 `toggle_favorite(user_id, restaurant_id)`。若原本已收藏則刪除記錄；若無則新增記錄。
* **輸出格式**：
  * **成功 (200 OK)**：
    `{"status": "success", "is_favorited": true/false, "message": "已加入最愛！"}`
  * **未授權 (401 Unauthorized)**：
    `{"status": "error", "message": "請先登入再進行收藏！"}`

---

### 2.3 發布評論 API (`POST /api/reviews/add`)
* **輸入參數**：
  * `restaurant_id` (JSON Payload)
  * `rating` (JSON Payload): 1 至 5 星整數。
  * `comment` (JSON Payload): 文字評論字串。
* **處理邏輯**：
  1. 檢查 Session 登入狀態，未登入回傳 401。
  2. 呼叫 `add_review(user_id, restaurant_id, rating, comment)` 將評價寫入 SQLite。
  3. 呼叫 `get_restaurant_reviews(restaurant_id)` 獲取最新評論清單。
* **輸出格式**：
  * **成功 (200 OK)**：
    `{"status": "success", "message": "評論已成功發布！", "reviews": [...]}`

---

## 3. Jinja2 HTML 模板規劃 (Templates Structure)

本系統全面套用響應式佈局 (RWD) 與毛玻璃風格 (Glassmorphism)，各頁面模板結構規劃如下：

### 3.1 基礎共享模板：`app/templates/base.html`
* **職責**：提供網站的整體視覺框架。
* **包含內容**：
  * 全域 Header：毛玻璃頂部導航欄（Navbar），動態根據登入狀態呈現「首頁、我的收藏、評論紀錄、登出」或「登入、註冊」按鈕。
  * Flash 提示訊息通知區。
  * 全域 Footer。
  * 公共 CSS 樣式庫及 FontAwesome 圖示 CDN 載入。

### 3.2 功能子模板清單
* **首頁 (`index.html`)**：
  * 繼承 `base.html` 的 `{% block content %}`。
  * 包含主隨機決策畫面、進階篩選隱藏面板、Premium 結果卡片（狀態呼吸燈、GPS 距離、招牌 Tag）、無刷新愛心收藏按鈕與評價提交區。
* **我的最愛頁 (`favorites.html`)**：
  * 繼承 `base.html`。
  * 包含收藏網格與「從我的最愛抽一家」大按鈕，彈出金色皇冠推薦結果卡片。
* **評價紀錄頁 (`reviews.html`)**：
  * 繼承 `base.html`。
  * 以毛玻璃 Timeline 時間軸形式，展示用戶發表過的所有評價與給予星等，並支援一鍵 AJAX 刪除評論。
* **認證登入頁 (`login.html`) / 註冊頁 (`register.html`)**：
  * 繼承 `base.html`。
  * 呈現毛玻璃裝飾的簡潔極美認證表單。

---

## 4. 路由骨架規劃 (Routes Skeleton Layout)

為配合專案的模組化架構，我們在 `app/routes/` 套件包中建立了乾淨的模組化骨架檔案。這些檔案以 pure 骨架（只含 Route 裝飾器、函式定義與 Docstring 說明，不寫具體邏輯）形式儲存，以利團隊後續的擴充開發。

```text
app/routes/
├── __init__.py         # 統一匯出介面，在當前階段負責無縫橋接伺服器正常運作
├── auth.py             # 會員註冊、登入與登出路由骨架
├── recommendation.py   # 條件隨機推薦 API 路由骨架
├── favorite.py         # 最愛展示、切換收藏與最愛抽選 API 路由骨架
└── review.py           # 歷史評論 Timeline、新增評論與刪除評論 API 路由骨架
```

### 4.1 骨架設計特點
* 所有的 URL 設計嚴格符合 RESTful 命名規範，採用名詞加 HTTP Method 的組合。
* 各路由與 `app/models/` 所拆分出的模組（`user.py`, `restaurant.py`, `favorite.py`, `review.py`）形成一對一的高內聚對應，方便未來擴充。
* 保留了最乾淨的註解說明，開發者能一眼看清每個 API 的輸入、邏輯處理與輸出回傳格式。
