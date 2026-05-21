# 隨便吃什麼都好 — 流程圖設計文件 (FLOWCHART.md)

> 本文件依據 `docs/PRD.md` 的功能需求與 `docs/ARCHITECTURE.md` 的系統架構，以 Mermaid 語法呈現使用者操作路徑與系統內部資料流，適合放入報告或簡報中使用。

---

## 1. 使用者流程圖（User Flow）

描述使用者從進入網站到完成各主要功能的完整操作路徑。

```mermaid
flowchart LR
    Start([🌐 使用者開啟網站]) --> Home[首頁\n隨機抽選頁面]

    Home --> SetFilter{設定篩選條件\n距離 / 價格 / 類型}
    SetFilter --> ClickSpin[點擊「開始隨機抽選」]
    ClickSpin --> SpinAnim[🎲 轉盤動畫旋轉]
    SpinAnim --> HasResult{有符合條件\n的餐廳？}
    HasResult -->|否| ErrorToast[顯示 Toast 警告\n「請放寬篩選條件」]
    ErrorToast --> SetFilter
    HasResult -->|是| ShowCard[顯示推薦餐廳卡片\n名稱 / 類型 / 評分 / 地址]

    ShowCard --> FavAction{點擊收藏❤️？}
    FavAction -->|是，未登入| LoginPage[導向登入頁]
    FavAction -->|是，已登入| FavToggle[AJAX 切換收藏狀態\n顯示 Toast 通知]
    FavAction -->|否| SkipFav[ ]

    ShowCard --> DetailLink[點擊「查看詳細評論」]
    DetailLink --> DetailPage[餐廳詳情頁\n地址 / 評分 / Google 地圖連結]
    DetailPage --> ReviewForm{填寫評論與星等？}
    ReviewForm -->|已登入| SubmitReview[送出評論\n動態更新平均評分]
    ReviewForm -->|未登入| LoginPage

    Home --> NavNearby[導覽列：附近餐廳]
    NavNearby --> NearbyFilter[篩選面板\n距離 / 類型 / 最低評分 / 搜尋關鍵字]
    NearbyFilter --> NearbyList[顯示符合條件的餐廳卡片網格]
    NearbyList --> DetailLink

    Home --> NavVote[導覽列：多人投票]
    NavVote --> VoteLobby[投票大廳\n發起投票表單]
    VoteLobby --> CreateRoom[建立投票房間\n隨機抽選候選餐廳]
    CreateRoom --> RoomPage[投票房間頁\n顯示候選餐廳 + 票數 Progress Bar]
    RoomPage --> ShareLink[複製房間連結\n分享給朋友]
    ShareLink --> FriendVote[朋友開啟連結\n點擊喜愛的餐廳投票]
    FriendVote --> CastVote{已投過票？}
    CastVote -->|是| DuplicateWarn[顯示「您已投過票」提示]
    CastVote -->|否| UpdateBar[更新票數 Progress Bar\n每 3 秒 AJAX 輪詢]

    Home --> NavAuth{已登入？}
    NavAuth -->|否| LoginPage
    NavAuth -->|是| NavFav[導覽列：我的收藏]
    NavAuth -->|是| NavHistory[導覽列：歷史紀錄]
    NavFav --> FavPage[收藏清單卡片網格\nAJAX 點擊取消收藏 → 卡片淡出移除]
    NavHistory --> HistoryPage[歷史紀錄雙分頁表格\n「抽選紀錄」與「我的評論」]

    LoginPage --> LoginForm[填寫帳號密碼]
    LoginForm --> LoginCheck{驗證成功？}
    LoginCheck -->|否| LoginError[顯示錯誤訊息]
    LoginCheck -->|是| Home
    LoginPage --> RegisterLink[點擊「立即註冊」]
    RegisterLink --> RegisterForm[填寫帳號 / 密碼]
    RegisterForm --> RegisterCheck{帳號已存在？}
    RegisterCheck -->|是| RegisterError[顯示「帳號已存在」]
    RegisterCheck -->|否| AutoLogin[自動登入 → 返回首頁]
```

---

## 2. 系統序列圖（Sequence Diagrams）

以下為各主要功能的後端資料流序列圖，描述從使用者操作到資料庫完成的完整步驟。

### 2.1 隨機抽選（/spin）

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route\n(routes/main.py)
    participant Model as SQLAlchemy Model\n(models/restaurant.py)
    participant DB as SQLite\n(instance/database.db)

    User->>Browser: 設定篩選條件，點擊「開始隨機抽選」
    Browser->>Browser: 播放轉盤旋轉動畫
    Browser->>Flask: POST /spin\n(JSON: distance, price_level, cuisines)
    Flask->>Model: 查詢符合條件的餐廳\nRestaurant.query.filter(...)
    Model->>DB: SELECT * FROM restaurants WHERE...
    DB-->>Model: 回傳符合條件的餐廳列表
    Model-->>Flask: restaurants list

    alt 找到符合條件的餐廳
        Flask->>Flask: random.choice(restaurants)
        Flask->>Model: 查詢是否已收藏\nFavorite.query.filter_by(user_id, restaurant_id)
        Model->>DB: SELECT * FROM favorites WHERE...
        DB-->>Model: 有 / 無收藏紀錄
        Flask->>DB: INSERT INTO spin_history\n（若使用者已登入）
        Flask-->>Browser: JSON: {id, name, category, rating, favorited, ...}
    else 找不到符合條件的餐廳
        Flask-->>Browser: 404 JSON: {error: "找不到符合條件..."}
    end

    Browser->>Browser: 停止動畫，顯示結果卡片與 Toast 通知
```

### 2.2 收藏切換（AJAX /favorite/toggle）

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route\n(routes/profile.py)
    participant Model as SQLAlchemy Model\n(models/favorite.py)
    participant DB as SQLite

    User->>Browser: 點擊收藏❤️ 按鈕
    Browser->>Flask: POST /favorite/toggle\n(JSON: restaurant_id)

    alt 使用者未登入
        Flask-->>Browser: 401 Unauthorized
        Browser->>Browser: Toast 警告「請先登入」\n3 秒後導向 /auth/login
    else 使用者已登入
        Flask->>Model: 查詢 Favorite.query.filter_by(user_id, restaurant_id)
        Model->>DB: SELECT * FROM favorites WHERE...
        DB-->>Model: 有 / 無紀錄

        alt 尚未收藏
            Flask->>DB: INSERT INTO favorites
            Flask-->>Browser: JSON: {status: "success", favorited: true}
            Browser->>Browser: 按鈕變為實心紅心 ❤️\nToast: 「已成功加入收藏」
        else 已收藏
            Flask->>DB: DELETE FROM favorites WHERE...
            Flask-->>Browser: JSON: {status: "success", favorited: false}
            Browser->>Browser: 按鈕變為空心愛心 🤍\nToast: 「已移除收藏」\n（若在收藏頁，卡片淡出消失）
        end
    end
```

### 2.3 提交評論與評分

```mermaid
sequenceDiagram
    actor User as 使用者（已登入）
    participant Browser as 瀏覽器
    participant Flask as Flask Route\n(routes/restaurant.py)
    participant ReviewModel as Model\n(models/review.py)
    participant RestModel as Model\n(models/restaurant.py)
    participant DB as SQLite

    User->>Browser: 在詳情頁選擇星等、填寫評論，送出表單
    Browser->>Flask: POST /restaurant/<id>/review\n(Form: rating, comment)
    Flask->>ReviewModel: 建立 Review 物件並寫入
    ReviewModel->>DB: INSERT INTO reviews
    DB-->>ReviewModel: 成功
    Flask->>RestModel: 重新計算平均評分\ndb.session.query(avg(Review.rating))
    RestModel->>DB: SELECT AVG(rating) FROM reviews WHERE restaurant_id=<id>
    DB-->>RestModel: 新的平均評分
    Flask->>DB: UPDATE restaurants SET rating=<新平均> WHERE id=<id>
    Flask-->>Browser: 302 Redirect → GET /restaurant/<id>
    Browser->>Flask: GET /restaurant/<id>
    Flask-->>Browser: 渲染更新後的詳情頁（含新評論與評分）
```

### 2.4 多人投票（建立房間與投票）

```mermaid
sequenceDiagram
    actor Host as 發起人
    actor Guest as 朋友（訪客）
    participant Browser as 瀏覽器
    participant Flask as Flask Route\n(routes/vote.py)
    participant VoteModel as Model\n(models/vote.py)
    participant DB as SQLite

    Host->>Browser: 在大廳設定人數，點擊「發起投票」
    Browser->>Flask: POST /vote/create
    Flask->>Flask: 隨機抽選 N 間候選餐廳
    Flask->>DB: INSERT INTO vote_rooms + INSERT INTO vote_options
    DB-->>Flask: room_id
    Flask-->>Browser: 302 Redirect → GET /vote/<room_id>
    Browser->>Host: 顯示投票房間（含分享連結）

    Host->>Guest: 複製房間連結並分享
    Guest->>Browser: 開啟 GET /vote/<room_id>
    Flask-->>Browser: 渲染房間頁（各候選餐廳 + 當前票數）

    Guest->>Browser: 點擊喜愛的餐廳投票
    Browser->>Flask: POST /vote/<room_id>/cast\n(JSON: option_id)
    Flask->>Flask: 檢查 Cookie 是否已投票過此房間

    alt 已投票過
        Flask-->>Browser: JSON: {error: "您已投過票了"}
    else 尚未投票
        Flask->>DB: UPDATE vote_options SET votes=votes+1
        Flask->>Browser: 設定 Cookie (voted_<room_id>=true)
        Flask-->>Browser: JSON: {status: "success"}
    end

    Browser->>Browser: 每 3 秒 AJAX 輪詢\nGET /vote/<room_id>/results
    Flask->>DB: SELECT * FROM vote_options WHERE room_id=<id>
    DB-->>Flask: 各選項得票數
    Flask-->>Browser: JSON: [{option_id, name, votes, percent}, ...]
    Browser->>Browser: 更新各候選餐廳的票數 Progress Bar
```

---

## 3. 功能清單對照表

| 功能名稱 | URL 路徑 | HTTP 方法 | 登入要求 | 說明 |
|---|---|---|---|---|
| 首頁（抽選頁） | `/` | GET | 否 | 渲染首頁，載入所有餐廳類別供篩選 |
| 隨機抽選 | `/spin` | POST | 否（登入才記錄歷史） | 依條件隨機抽選餐廳，回傳 JSON |
| 附近餐廳探索 | `/nearby` | GET | 否 | 條件篩選餐廳列表（距離/類型/評分/關鍵字） |
| 餐廳詳情頁 | `/restaurant/<id>` | GET | 否 | 顯示餐廳資訊、評分與所有評論 |
| 提交餐廳評論 | `/restaurant/<id>/review` | POST | **是** | 提交評論並自動重算平均評分 |
| 會員登入 | `/auth/login` | GET / POST | 否 | 顯示表單（GET）/ 驗證登入（POST） |
| 會員註冊 | `/auth/register` | GET / POST | 否 | 顯示表單（GET）/ 建立帳號（POST） |
| 登出 | `/auth/logout` | POST | **是** | 清除 Flask-Login Session |
| 我的收藏 | `/profile/favorites` | GET | **是** | 顯示使用者收藏的餐廳卡片網格 |
| 收藏切換（AJAX） | `/favorite/toggle` | POST | **是** | 新增或取消收藏，回傳 JSON |
| 歷史紀錄 | `/profile/history` | GET | **是** | 顯示抽選紀錄與評論歷程雙分頁 |
| 投票大廳 | `/vote` | GET | 否 | 顯示發起投票表單 |
| 建立投票房間 | `/vote/create` | POST | 否 | 隨機選出候選餐廳，建立投票房間 |
| 投票房間 | `/vote/<room_id>` | GET | 否 | 顯示候選餐廳與即時票數 |
| 送出投票 | `/vote/<room_id>/cast` | POST | 否（Cookie 防灌票） | 為指定選項加票，回傳 JSON |
| 查詢即時票數 | `/vote/<room_id>/results` | GET | 否 | 回傳各選項票數 JSON（每 3 秒輪詢） |
