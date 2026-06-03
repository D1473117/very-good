# 隨便吃什麼都好 — 路由設計文件 (ROUTES.md)

> 本文件依據 `docs/PRD.md`、`docs/ARCHITECTURE.md` 與 `docs/DB_DESIGN.md`，完整說明系統所有 Flask Blueprint 路由的 URL、HTTP 方法、輸入輸出與對應的 Jinja2 模板。

---

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | Blueprint | 對應模板 | 登入要求 |
|---|---|---|---|---|---|
| **首頁（轉盤抽選）** | GET | `/` | `main` | `index.html` | 否 |
| **隨機抽選 API** | POST | `/spin` | `main` | — (JSON) | 否（登入才記錄歷史） |
| **附近餐廳探索** | GET | `/nearby` | `main` | `main/nearby.html` | 否 |
| **餐廳詳情頁** | GET | `/restaurant/<int:id>` | `restaurant` | `restaurant/detail.html` | 否 |
| **提交評論** | POST | `/restaurant/<int:id>/review` | `restaurant` | — (重導向) | **是** |
| **會員註冊頁面** | GET | `/auth/register` | `auth` | `auth/register.html` | 否 |
| **會員註冊（送出）** | POST | `/auth/register` | `auth` | — (重導向) | 否 |
| **會員登入頁面** | GET | `/auth/login` | `auth` | `auth/login.html` | 否 |
| **會員登入（送出）** | POST | `/auth/login` | `auth` | — (重導向) | 否 |
| **會員登出** | POST | `/auth/logout` | `auth` | — (重導向) | **是** |
| **我的收藏** | GET | `/profile/favorites` | `profile` | `profile/favorites.html` | **是** |
| **歷史紀錄** | GET | `/profile/history` | `profile` | `profile/history.html` | **是** |
| **收藏切換（AJAX）** | POST | `/favorite/toggle` | `profile` | — (JSON) | **是** |
| **投票大廳** | GET | `/vote` | `vote` | `vote/lobby.html` | 否 |
| **建立投票房間** | POST | `/vote/create` | `vote` | — (重導向) | 否 |
| **投票房間** | GET | `/vote/<room_id>` | `vote` | `vote/room.html` | 否 |
| **送出投票** | POST | `/vote/<room_id>/cast` | `vote` | — (重導向) | 否（Cookie 防灌票） |
| **即時票數查詢（AJAX）** | GET | `/vote/<room_id>/data` | `vote` | — (JSON) | 否 |

---

## 2. 每個路由的詳細說明

### Blueprint: `main` — 核心頁面（`app/routes/main.py`）

---

#### `GET /` — 首頁

- **函式名稱**：`index()`
- **輸入**：無
- **處理邏輯**：
  1. 查詢 `restaurants` 資料表中所有不重複的 `category` 欄位值
  2. 將類別清單傳入模板，供使用者勾選篩選條件
- **輸出**：渲染 `templates/index.html`，傳入變數 `categories: list[str]`
- **錯誤處理**：無（資料表為空時 categories 為空清單，正常渲染）

---

#### `POST /spin` — 隨機抽選 API（AJAX）

- **函式名稱**：`spin()`
- **輸入（JSON Body）**：
  | 欄位 | 型別 | 說明 | 預設值 |
  |---|---|---|---|
  | `distance` | int | 最大距離（公尺） | 3000 |
  | `price_level` | list[int] | 可接受的價格等級（1~4） | [1,2,3,4] |
  | `cuisines` | list[str] | 要篩選的料理類型 | []（不限） |
- **處理邏輯**：
  1. 以條件過濾 `Restaurant` 資料表（距離、價格等級、料理類型）
  2. 若無符合結果，回傳 404
  3. `random.choice()` 隨機選取一筆餐廳
  4. 若使用者已登入：查詢是否已收藏（`favorited`），並新增 `SpinHistory` 紀錄
  5. 回傳餐廳資料 JSON（含 `favorited` 欄位）
- **輸出（JSON）**：
  ```json
  {
    "id": 2, "name": "屋馬燒肉", "category": "日式",
    "rating": 4.8, "price_level": 3, "distance": 1500,
    "address": "台中市...", "lat": null, "lng": null,
    "favorited": false
  }
  ```
- **錯誤處理**：
  - 找不到符合條件的餐廳 → `404 {"error": "找不到符合條件的餐廳..."}`

---

#### `GET /nearby` — 附近餐廳探索

- **函式名稱**：`nearby()`
- **輸入（URL Query 參數）**：
  | 參數 | 型別 | 說明 |
  |---|---|---|
  | `search` | str | 搜尋關鍵字（餐廳名稱或地址模糊比對） |
  | `distance` | int | 最大距離過濾 |
  | `category` | str | 料理類型過濾 |
  | `rating` | float | 最低評分過濾 |
- **處理邏輯**：
  1. 依有傳入的參數動態組合 SQLAlchemy 查詢條件
  2. 若使用者已登入，取得其所有收藏的 `restaurant_id` 集合（`fav_ids`），供模板顯示愛心狀態
- **輸出**：渲染 `templates/main/nearby.html`，傳入 `restaurants`、`categories`、`fav_ids` 等變數
- **錯誤處理**：無符合結果時，模板顯示「找不到餐廳」提示

---

### Blueprint: `restaurant` — 餐廳詳情（`app/routes/restaurant.py`）

---

#### `GET /restaurant/<int:restaurant_id>` — 餐廳詳情頁

- **函式名稱**：`detail(restaurant_id)`
- **輸入**：URL 路徑參數 `restaurant_id`（整數）
- **處理邏輯**：
  1. 以 `Restaurant.query.get_or_404()` 取得餐廳，不存在則自動回傳 404
  2. 取得該餐廳的所有評論（依 `created_at` 降冪排序）
  3. 若使用者已登入，查詢是否已收藏
- **輸出**：渲染 `templates/restaurant/detail.html`，傳入 `restaurant`、`reviews`、`favorited`
- **錯誤處理**：餐廳不存在 → Flask 自動 abort(404)

---

#### `POST /restaurant/<int:restaurant_id>/review` — 提交評論

- **函式名稱**：`submit_review(restaurant_id)`
- **輸入（Form Data）**：
  | 欄位 | 說明 |
  |---|---|
  | `rating` | 評分（1.0 ~ 5.0） |
  | `comment` | 評論內文（必填） |
- **處理邏輯**：
  1. 登入驗證（`@login_required`）
  2. 防止同一使用者對同一餐廳重複評論
  3. 驗證評分範圍是否在 1.0 ~ 5.0 之間
  4. 新增 `Review` 資料後，重新計算該餐廳所有評論的平均評分，並更新 `restaurants.rating`
- **輸出**：Flash 成功訊息 + 重導向回 `GET /restaurant/<id>`
- **錯誤處理**：未登入 → 導向登入頁；重複評論 / 格式錯誤 → Flash 警告並重導向回詳情頁

---

### Blueprint: `auth` — 會員驗證（`app/routes/auth.py`）

---

#### `GET /auth/register` — 顯示註冊表單
#### `POST /auth/register` — 送出註冊

- **函式名稱**：`register()`
- **POST 輸入（Form Data）**：`username`、`password`、`confirm_password`
- **處理邏輯**：
  1. GET：若已登入則重導向首頁
  2. POST：驗證欄位不為空、密碼長度 ≥ 6、兩次密碼相符
  3. 確認 username 未被使用
  4. 建立 `User`，以 `set_password()` 進行 Bcrypt Hash
  5. 使用 `login_user()` 自動登入
- **輸出**：POST 成功 → Flash 歡迎訊息 + 重導向首頁；驗證失敗 → Flash 錯誤 + 重新渲染表單

---

#### `GET /auth/login` — 顯示登入表單
#### `POST /auth/login` — 送出登入

- **函式名稱**：`login()`
- **POST 輸入（Form Data）**：`username`、`password`、`remember`（checkbox）
- **處理邏輯**：
  1. 查詢 User，以 `check_password()` 驗證 Bcrypt Hash
  2. 驗證成功 → `login_user(user, remember=remember)` 建立 Session
- **輸出**：POST 成功 → Flash 歡迎訊息 + 重導向首頁；驗證失敗 → Flash 錯誤 + 重新渲染

---

#### `POST /auth/logout` — 登出

- **函式名稱**：`logout()`
- **處理邏輯**：呼叫 `logout_user()` 清除 Session
- **輸出**：Flash 訊息 + 重導向首頁

---

### Blueprint: `profile` — 會員中心（`app/routes/profile.py`）

---

#### `GET /profile/favorites` — 我的收藏

- **函式名稱**：`favorites()`
- **輸入**：無（從 `current_user` 取得 user_id）
- **處理邏輯**：查詢 `Favorite` 並透過 relationship 取出對應的 `Restaurant` 物件清單
- **輸出**：渲染 `templates/profile/favorites.html`，傳入 `restaurants: list[Restaurant]`

---

#### `GET /profile/history` — 歷史紀錄

- **函式名稱**：`history()`
- **輸入**：無
- **處理邏輯**：分別查詢 `SpinHistory`（抽選紀錄）與 `Review`（評論紀錄），依時間降冪排列
- **輸出**：渲染 `templates/profile/history.html`，傳入 `spins`、`reviews`

---

#### `POST /favorite/toggle` — 收藏切換（AJAX）

- **函式名稱**：`toggle_favorite()`
- **輸入（JSON Body）**：`restaurant_id: int`
- **處理邏輯**：
  1. 手動驗證登入（不用 `@login_required`，以便 AJAX 取得 401 JSON 而非 HTML 重導向）
  2. 查詢 Favorite 是否存在 → 存在則刪除，不存在則新增
- **輸出（JSON）**：
  ```json
  { "status": "success", "favorited": true }
  ```
- **錯誤處理**：
  - 未登入 → `401 {"error": "請先登入後再進行此操作！"}`
  - 未傳入 / 無效的 restaurant_id → `400 {"error": "..."}`
  - 找不到餐廳 → `404 {"error": "找不到指定的餐廳"}`

---

### Blueprint: `vote` — 多人投票（`app/routes/vote.py`）

---

#### `GET /vote` — 投票大廳

- **函式名稱**：`lobby()`
- **處理邏輯**：查詢最近 10 個投票房間
- **輸出**：渲染 `templates/vote/lobby.html`，傳入 `rooms`

---

#### `POST /vote/create` — 建立投票房間

- **函式名稱**：`create_room()`
- **輸入（Form Data）**：`title`（投票主題，選填）
- **處理邏輯**：
  1. 若未填 title，使用預設標題
  2. 從 `restaurants` 隨機抽選最多 4 間作為候選
  3. 建立 `VoteRoom`（UUID 短碼 PK）與對應的 `VoteOption`
- **輸出**：Flash 成功訊息 + 重導向至 `GET /vote/<room_id>`

---

#### `GET /vote/<room_id>` — 投票房間頁

- **函式名稱**：`room(room_id)`
- **輸入**：URL 路徑參數 `room_id`（8 碼 UUID 字串）
- **處理邏輯**：
  1. 取得房間與所有選項，計算總票數
  2. 透過 Cookie（`voted_<room_id>`）或 Session 判斷當前瀏覽器是否已投票
- **輸出**：渲染 `templates/vote/room.html`，傳入 `room`、`options`、`total_votes`、`has_voted`

---

#### `POST /vote/<room_id>/cast` — 送出投票

- **函式名稱**：`cast_vote(room_id)`
- **輸入（Form Data）**：`option_id: int`
- **處理邏輯**：
  1. 檢查 Cookie / Session，若已投票則 Flash 警告並重導向
  2. 驗證 option_id 有效且屬於此房間
  3. `option.votes += 1` 並 commit
  4. 設定 Cookie（`max_age=7天`）與 Session 標記
- **輸出**：Flash 成功訊息 + 重導向回投票房間頁

---

#### `GET /vote/<room_id>/data` — 即時票數 AJAX API

- **函式名稱**：`room_data(room_id)`
- **輸入**：URL 路徑參數 `room_id`
- **輸出（JSON）**：
  ```json
  {
    "room_title": "今天吃什麼？美味對決！",
    "total_votes": 12,
    "options": [
      { "option_id": 1, "restaurant_name": "屋馬燒肉", "votes": 7, "percentage": 58.3 },
      { "option_id": 2, "restaurant_name": "輕井澤鍋物", "votes": 5, "percentage": 41.7 }
    ]
  }
  ```
- **錯誤處理**：找不到房間 → `404 {"error": "Room not found"}`

---

## 3. Jinja2 模板清單

所有模板均繼承自 `app/templates/base.html`。

| 模板路徑 | 對應路由 | 功能說明 |
|---|---|---|
| `templates/base.html` | — | 基底模板（導覽列、Flash 訊息、頁尾、Toast 容器） |
| `templates/index.html` | `GET /` | 首頁：條件篩選面板 + 輪盤轉動動畫 + 結果卡片 |
| `templates/main/nearby.html` | `GET /nearby` | 附近探索：左側篩選面板 + 右側餐廳卡片網格 |
| `templates/restaurant/detail.html` | `GET /restaurant/<id>` | 餐廳詳情：資訊卡片、評分星等、評論列表、留評表單 |
| `templates/auth/register.html` | `GET /auth/register` | 會員註冊表單（Glassmorphism 卡片樣式） |
| `templates/auth/login.html` | `GET /auth/login` | 會員登入表單（含「記住我」checkbox） |
| `templates/profile/favorites.html` | `GET /profile/favorites` | 收藏清單：卡片網格，AJAX 點擊移除 |
| `templates/profile/history.html` | `GET /profile/history` | 歷史紀錄：「抽選紀錄」與「我的評論」雙分頁表格 |
| `templates/vote/lobby.html` | `GET /vote` | 投票大廳：發起投票表單 + 最近房間清單 |
| `templates/vote/room.html` | `GET /vote/<room_id>` | 投票房間：候選餐廳卡片 + Progress Bar 計票 |

---

## 4. 路由骨架程式碼（帶 Docstring）

> 以下骨架為說明用，**實際實作已完整存在於 `app/routes/` 各檔案中**。

### `app/routes/main.py`

```python
from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    首頁路由。
    從資料庫動態讀取所有不重複的餐廳類別（category），
    傳入 index.html 供使用者勾選條件。
    回傳：render_template('index.html', categories=categories)
    """
    pass

@main_bp.route('/spin', methods=['POST'])
def spin():
    """
    AJAX 隨機抽選 API（JSON 輸入/輸出）。
    接收 distance、price_level、cuisines 條件，
    過濾並隨機選取一筆符合的餐廳。
    登入使用者額外記錄 SpinHistory 並回傳 favorited 狀態。
    回傳：jsonify(restaurant_dict + favorited)
    錯誤：404 若找不到符合條件的餐廳
    """
    pass

@main_bp.route('/nearby')
def nearby():
    """
    附近餐廳探索頁（GET 參數過濾）。
    接收 search、distance、category、rating 等 Query 參數，
    動態組合 SQLAlchemy 查詢，並傳入已登入使用者的收藏 ID 集合。
    回傳：render_template('main/nearby.html', ...)
    """
    pass
```

### `app/routes/auth.py`

```python
from flask import Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    """
    GET：顯示會員註冊表單（已登入者重導向首頁）。
    POST：驗證欄位 → 確認 username 唯一 → 以 Bcrypt Hash 密碼建立 User
          → login_user() 自動登入 → 重導向首頁。
    錯誤：Flash 提示（欄位空白、密碼不符、帳號已存在）
    """
    pass

@auth_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    """
    GET：顯示會員登入表單（已登入者重導向首頁）。
    POST：查詢 User → check_password() 驗證 Bcrypt Hash
          → login_user(remember=...) → 重導向首頁。
    錯誤：Flash「使用者名稱或密碼錯誤」
    """
    pass

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    登出目前使用者，清除 Flask-Login Session。
    回傳：Flash 訊息 + 重導向首頁
    """
    pass
```

### `app/routes/restaurant.py`

```python
from flask import Blueprint
restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/restaurant/<int:restaurant_id>')
def detail(restaurant_id):
    """
    餐廳詳情頁。
    取得餐廳資料與所有評論（降冪排序），
    若已登入則附帶 favorited 狀態。
    回傳：render_template('restaurant/detail.html', ...)
    錯誤：404 若 restaurant_id 不存在
    """
    pass

@restaurant_bp.route('/restaurant/<int:restaurant_id>/review', methods=['POST'])
def submit_review(restaurant_id):
    """
    提交餐廳評論（需登入）。
    驗證 rating(1~5) 與 comment 非空，
    防止同一使用者重複評論，
    新增評論後重新計算並更新餐廳平均評分。
    回傳：重導向回詳情頁（Flash 成功/錯誤訊息）
    """
    pass
```

### `app/routes/profile.py`

```python
from flask import Blueprint
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/favorites')
def favorites():
    """
    我的收藏頁（需登入）。
    查詢當前使用者的所有 Favorite 紀錄，
    透過 relationship 取出對應的 Restaurant 物件。
    回傳：render_template('profile/favorites.html', restaurants=...)
    """
    pass

@profile_bp.route('/profile/history')
def history():
    """
    歷史紀錄頁（需登入）。
    查詢當前使用者的 SpinHistory（抽選紀錄）與 Review（評論紀錄），
    分別降冪排序後傳入模板。
    回傳：render_template('profile/history.html', spins=..., reviews=...)
    """
    pass

@profile_bp.route('/favorite/toggle', methods=['POST'])
def toggle_favorite():
    """
    收藏切換 AJAX API（需登入）。
    接收 JSON body: {restaurant_id}，
    查詢 Favorite 是否存在 → 存在則刪除，不存在則新增。
    以手動方式驗證登入（回傳 401 JSON，而非 HTML 重導向）。
    回傳：jsonify({status, favorited})
    錯誤：401（未登入）/ 400（無效 ID）/ 404（餐廳不存在）
    """
    pass
```

### `app/routes/vote.py`

```python
from flask import Blueprint
vote_bp = Blueprint('vote', __name__)

@vote_bp.route('/vote')
def lobby():
    """
    投票大廳頁。
    顯示最近 10 個投票房間與「發起投票」表單。
    回傳：render_template('vote/lobby.html', rooms=...)
    """
    pass

@vote_bp.route('/vote/create', methods=['POST'])
def create_room():
    """
    建立投票房間。
    從所有餐廳中隨機抽選最多 4 間為候選，
    建立 VoteRoom（UUID 短碼）與對應的 VoteOption。
    回傳：重導向至 GET /vote/<room_id>
    """
    pass

@vote_bp.route('/vote/<room_id>')
def room(room_id):
    """
    投票房間頁。
    展示候選餐廳選項與目前票數，
    透過 Cookie/Session 判斷當前瀏覽器是否已投票。
    回傳：render_template('vote/room.html', ...)
    錯誤：404 若 room_id 不存在
    """
    pass

@vote_bp.route('/vote/<room_id>/cast', methods=['POST'])
def cast_vote(room_id):
    """
    送出投票。
    防灌票（Cookie + Session 雙重驗證）→ 驗證 option_id 有效
    → votes += 1 → 設定 Cookie（7天）與 Session 標記。
    回傳：Flash 訊息 + 重導向回投票房間頁
    """
    pass

@vote_bp.route('/vote/<room_id>/data')
def room_data(room_id):
    """
    即時票數查詢 AJAX API（每 3 秒輪詢）。
    回傳各選項票數與百分比 JSON，供前端更新 Progress Bar。
    回傳：jsonify({room_title, total_votes, options: [...]})
    錯誤：404 若房間不存在
    """
    pass
```
