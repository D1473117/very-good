# API 路由與頁面設計文件 (docs/ROUTES.md)

本文件規劃了「隨便吃什麼都好」系統的 Flask 路由（Routes），包含每個頁面的 URL 路徑、HTTP 方法、輸入/輸出與對應的 Jinja2 模板，並遵守 RESTful 規格設計。

---

## 1. 路由總覽表格

| 功能分類 | 功能名稱 | HTTP 方法 | URL 路徑 | 對應模板/輸出 | 說明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **主畫面** | 首頁/抽選畫面 | GET | `/` | `index.html` | 顯示首頁，包含條件篩選與「抽！」按鈕 |
| | 執行隨機抽選 | POST | `/spin` | 重導向 或 JSON | 接收篩選條件，隨機推薦餐廳，登入者自動寫入歷史紀錄 |
| | 附近餐廳列表 | GET | `/nearby` | `nearby.html` | 顯示附近一定距離內餐廳，依距離排序 |
| **會員管理** | 註冊頁面 | GET | `/auth/register` | `auth/register.html` | 顯示使用者註冊表單 |
| | 處理註冊 | POST | `/auth/register` | 重導向 `/auth/login` | 接收註冊表單，驗證後寫入資料庫 |
| | 登入頁面 | GET | `/auth/login` | `auth/login.html` | 顯示使用者登入表單 |
| | 處理登入 | POST | `/auth/login` | 重導向 `/` | 驗證使用者帳密，建立 Session |
| | 處理登出 | POST | `/auth/logout` | 重導向 `/` | 清除 Session 並登出 |
| **餐廳資訊** | 餐廳詳細資訊 | GET | `/restaurant/<int:id>` | `restaurant_detail.html` | 顯示單筆餐廳之完整資訊 |
| **個人中心** | 我的收藏列表 | GET | `/profile/favorites` | `profile/favorites.html` | 顯示使用者收藏之餐廳清單（需登入） |
| (F-05) | 切換收藏狀態 | POST | `/favorite/toggle` | JSON | AJAX 非同步收藏/取消收藏餐廳（需登入） |
| | 推薦歷史紀錄 | GET | `/profile/history` | `profile/history.html` | 顯示使用者隨機推薦歷史紀錄（需登入，分頁） |
| | 清空歷史紀錄 | POST | `/profile/history/clear` | 重導向 `/profile/history`| 清空該使用者所有推薦歷史紀錄（需登入） |
| **多人投票** | 建立投票房間頁 | GET | `/vote/create` | `vote/create.html` | 顯示多人投票房間建立表單（Nice to Have） |
| (未來擴充) | 建立投票房間 | POST | `/vote/create` | 重導向房間頁面 | 建立投票房間並產生房號，重導向至房間 |
| | 進入投票房間 | GET | `/vote/room/<room_code>`| `vote/room.html` | 顯示多人投票房間，進行即時投票 |
| | 提交房間投票 | POST | `/vote/room/<room_code>/vote`| JSON | 提交投票（AJAX，回傳 JSON） |
| | 輪詢房間狀態 | GET | `/vote/room/<room_code>/status`| JSON | 取得房間目前投票狀態與結果（AJAX，回傳 JSON） |

---

## 2. 每個路由的詳細說明

### 2.1 主畫面模組 (`main`)

#### `GET /`
*   **說明**：顯示系統主頁（抽選主畫面）。
*   **輸入**：無。
*   **處理邏輯**：載入首頁，初始化預設篩選參數。
*   **輸出**：渲染 `index.html`。
*   **錯誤處理**：無。

#### `POST /spin`
*   **說明**：接收篩選條件，執行隨機推薦演算法。
*   **輸入**：
    *   表單或 JSON：`category`（類別，字串）、`price_range`（價格區間，字串）、`distance`（最大距離，整數）、`latitude`（經度，浮點數）、`longitude`（緯度，浮點數）。
*   **處理邏輯**：
    1.  根據類別、價格、距離篩選 `Restaurant` 資料。
    2.  利用隨機演算法（如 `random.choice()`）選出一間餐廳。
    3.  **若使用者已登入**：呼叫 `RecommendationHistory.create(user_id, restaurant_id)` 寫入歷史紀錄。
*   **輸出**：
    *   同步請求：重導向至 `/restaurant/<id>`。
    *   AJAX 請求：回傳 JSON `{ "status": "success", "restaurant_id": id }`。
*   **錯誤處理**：
    *   若無符合篩選條件的餐廳，重導向回首頁並以 Flash 訊息提示，或 AJAX 回傳 `{ "status": "error", "message": "找不到符合條件的餐廳" }`（HTTP 404）。

#### `GET /nearby`
*   **說明**：根據使用者 GPS 定位，顯示周邊餐廳列表。
*   **輸入**：
    *   URL 查詢參數：`lat`（緯度，必填）、`lng`（經度，必填）、`distance`（搜尋半徑公尺，預設 500）。
*   **處理邏輯**：
    1.  讀取所有餐廳，以 Haversine 公式計算各餐廳與該座標之距離。
    2.  過濾距離小於 `distance` 的餐廳。
    3.  將結果依距離由近到遠排序。
*   **輸出**：渲染 `nearby.html`。
*   **錯誤處理**：
    *   若參數不全或格式錯誤，顯示錯誤提示。

---

### 2.2 會員管理模組 (`auth`)

#### `GET /auth/register`
*   **說明**：顯示註冊頁面。
*   **輸入**：無。
*   **輸出**：渲染 `auth/register.html`。

#### `POST /auth/register`
*   **說明**：處理使用者註冊請求。
*   **輸入**：
    *   表單欄位：`username`（字串，必填）、`password`（字串，必填）、`confirm_password`（字串，必填）。
*   **處理邏輯**：
    1.  驗證欄位是否填妥、密碼與確認密碼是否一致。
    2.  檢查使用者名稱 `username` 是否已被註冊。
    3.  使用 bcrypt 進行密碼雜湊，寫入 `User` 資料庫。
*   **輸出**：重導向至 `/auth/login` 並 Flash 提示註冊成功。
*   **錯誤處理**：
    *   驗證失敗或名稱重複時，重新渲染 `auth/register.html`，並顯示對應錯誤訊息。

#### `GET /auth/login`
*   **說明**：顯示登入頁面。
*   **輸入**：無。
*   **輸出**：渲染 `auth/login.html`。

#### `POST /auth/login`
*   **說明**：驗證登入並建立 Session。
*   **輸入**：
    *   表單欄位：`username`（字串）、`password`（字串）。
*   **處理邏輯**：
    1.  根據 `username` 查詢使用者。
    2.  使用 bcrypt 比對密碼。
    3.  若正確，呼叫 Flask-Login 的 `login_user()` 建立登入狀態。
*   **輸出**：重導向至首頁 `/`。
*   **錯誤處理**：
    *   驗證失敗重新渲染 `auth/login.html`，並顯示「帳號或密碼錯誤」提示。

#### `POST /auth/logout`
*   **說明**：登出目前使用者並清除 Session。
*   **輸入**：無。
*   **處理邏輯**：呼叫 Flask-Login 的 `logout_user()`。
*   **輸出**：重導向至首頁 `/`。

---

### 2.3 餐廳資訊模組 (`restaurant`)

#### `GET /restaurant/<int:id>`
*   **說明**：顯示特定餐廳的詳細介紹頁面。
*   **輸入**：URL 參數 `id`（餐廳唯一識別碼）。
*   **處理邏輯**：
    1.  從資料庫查詢對應 `id` 的 `Restaurant` 資料。
    2.  若使用者已登入，呼叫 `Favorite.is_favorited(current_user.id, id)` 檢查是否已被收藏。
*   **輸出**：渲染 `restaurant_detail.html`，並傳入 `is_favorited` 變數。
*   **錯誤處理**：
    *   若餐廳不存在，回傳 HTTP 404 錯誤頁面。

---

### 2.4 個人中心與 F-05 模組 (`profile`)

#### `GET /profile/favorites`
*   **說明**：顯示目前登入用戶的收藏餐廳清單。
*   **安全防護**：加上 `@login_required`。
*   **輸入**：無。
*   **處理邏輯**：呼叫 `Favorite.get_by_user(current_user.id)` 獲取收藏記錄，透過 SQLAlchemy 關聯載入餐廳資訊。
*   **輸出**：渲染 `profile/favorites.html`。

#### `POST /favorite/toggle`
*   **說明**：非同步（AJAX）切換收藏狀態。
*   **安全防護**：加上 `@login_required`，且前端需傳遞 CSRF Token。
*   **輸入**：
    *   JSON 或表單：`restaurant_id`（餐廳 ID，整數，必填）。
*   **處理邏輯**：
    1.  驗證 `restaurant_id` 是否存在。
    2.  查詢 `Favorite` 表是否已有 `(current_user.id, restaurant_id)` 的記錄。
    3.  若**已存在**：呼叫 `Favorite.delete(current_user.id, restaurant_id)` 刪除紀錄。
    4.  若**不存在**：呼叫 `Favorite.create(current_user.id, restaurant_id)` 新增紀錄。
*   **輸出**：回傳 JSON `{ "status": "success", "favorited": true }`（新增）或 `{ "status": "success", "favorited": false }`（刪除）。
*   **錯誤處理**：
    *   未登入：回傳 JSON `{ "error": "unauthorized" }`（HTTP 401）。
    *   無效餐廳 ID：回傳 JSON `{ "error": "invalid_restaurant" }`（HTTP 400）。

#### `GET /profile/history`
*   **說明**：顯示目前登入用戶的推薦歷史紀錄。
*   **安全防護**：加上 `@login_required`。
*   **輸入**：
    *   URL 查詢參數：`page`（目前頁碼，預設 1）、`limit`（每頁幾筆，預設 10）。
*   **處理邏輯**：
    1.  呼叫 `RecommendationHistory.get_by_user(current_user.id, limit=limit, offset=(page-1)*limit)` 取得歷史紀錄。
    2.  計算總記錄數以供分頁元件（Pagination）渲染。
*   **輸出**：渲染 `profile/history.html`。

#### `POST /profile/history/clear`
*   **說明**：清空目前登入用戶的所有推薦歷史。
*   **安全防護**：加上 `@login_required`。
*   **輸入**：無。
*   **處理邏輯**：呼叫 `RecommendationHistory.clear_user_history(current_user.id)`。
*   **輸出**：重導向至 `/profile/history`，並 Flash 提示歷史紀錄已清空。

---

### 2.5 多人投票模組 (`vote` - Future Extension)

#### `GET /vote/create`
*   **說明**：顯示建立多人投票房間表單。
*   **輸出**：渲染 `vote/create.html`。

#### `POST /vote/create`
*   **說明**：建立投票房間，產生隨機房號。
*   **輸入**：表單欄位（地區、餐點類別、價格區間）。
*   **處理邏輯**：建立房間記錄，隨機抽取 3–5 間候選餐廳，產生 6 碼英數代碼，將發起人設為房主。
*   **輸出**：重導向至 `/vote/room/<room_code>`。

#### `GET /vote/room/<room_code>`
*   **說明**：進入投票房間，可進行投票或觀看結果。
*   **輸入**：URL 參數 `room_code`（6 碼房間代碼）。
*   **輸出**：渲染 `vote/room.html`。

#### `POST /vote/room/<room_code>/vote`
*   **說明**：提交使用者對某餐廳的投票。
*   **輸入**：表單或 JSON：`restaurant_id`。
*   **輸出**：回傳 JSON `{ "status": "success", "message": "投票成功" }`。

#### `GET /vote/room/<room_code>/status`
*   **說明**：輪詢（Polling）取得目前投票狀態與結果。
*   **輸出**：回傳 JSON `{ "votes": { restaurant_id: count }, "closed": true/false, "winner": restaurant_id }`。

---

## 3. Jinja2 模板清單

全站模板均繼承共用模板 `base.html`，以保持外觀一致與易維護性。

| 模板檔案路徑 | 繼承之父模板 | 說明 |
| :--- | :--- | :--- |
| `templates/base.html` | — (根模板) | 定義全站共用的 Layout（包含 Navbar、Footer、Bootstrap 與共用 JS 載入點） |
| `templates/index.html` | `base.html` | 首頁抽選主畫面（包含篩選條件表單與轉盤抽選動畫） |
| `templates/nearby.html` | `base.html` | 附近餐廳搜尋與列表展示頁面 |
| `templates/restaurant_detail.html` | `base.html` | 餐廳詳細資訊展示頁（包含 Google Maps 內嵌、詳細資訊與 AJAX 收藏按鈕） |
| `templates/auth/login.html` | `base.html` | 使用者登入畫面 |
| `templates/auth/register.html` | `base.html` | 使用者註冊畫面 |
| `templates/profile/favorites.html` | `base.html` | 個人中心：我的收藏餐廳卡片清單 |
| `templates/profile/history.html` | `base.html` | 個人中心：抽選歷史紀錄分頁表格（可快速收藏/取消收藏或清空歷史） |
| `templates/vote/create.html` | `base.html` | 建立多人投票房間頁面 |
| `templates/vote/room.html` | `base.html` | 多人投票房間主畫面，顯示倒數計時與即時得票結果 |

---

## 4. 路由骨架程式碼 (Skeleton)

已於 `app/routes/` 下建立以下模組的路由骨架檔案：
*   `app/routes/auth.py`
*   `app/routes/main.py`
*   `app/routes/restaurant.py`
*   `app/routes/profile.py`
*   `app/routes/vote.py`

*詳細路由函式簽名與註解請參閱 `app/routes/` 內的 Python 原始碼。*
