# 流程圖文件（Feature Flowchart）- F-05 收藏與歷史紀錄

**專案名稱：** 隨便吃什麼都好（Let's Just Eat）  
**功能模組：** F-05 收藏與歷史紀錄 (Favorites & Recommendation History)  
**對應主流程：** [docs/FLOWCHART.md](file:///c:/Users/USER/very-good/docs/FLOWCHART.md) (若有)  
**狀態：** 草稿  
**撰寫日期：** 2026-05-20  

---

## 1. 使用者流程圖（User Flow）
下圖描述使用者從進入首頁開始，進行隨機推薦（進而產生歷史紀錄與收藏操作），以及進入個人中心管理收藏清單與歷史紀錄的操作路徑。

```mermaid
flowchart LR
    Start([使用者開啟網頁]) --> Home[首頁 - 抽選主頁]
    
    Home --> Actions{選擇操作路徑}
    
    %% 路徑 A：抽選與收藏
    Actions -->|1. 點擊「抽！」| Spin[點擊隨機抽選]
    Spin --> CheckLogin1{已登入？}
    CheckLogin1 -->|是| WriteHist[系統自動寫入歷史紀錄] --> ShowRes[顯示推薦結果頁面]
    CheckLogin1 -->|否| ShowRes
    
    ShowRes --> ClickFav1[點擊收藏愛心]
    ClickFav1 --> CheckLogin2{已登入？}
    CheckLogin2 -->|是| ToggleFav1[AJAX 切換收藏狀態] --> UpdateUI1[更新愛心樣式 ❤️ / 🤍]
    CheckLogin2 -->|否| ToLogin[引導至登入頁]
    
    ShowRes --> ViewDetail[查看餐廳詳細資訊] --> ClickFav2[點擊收藏愛心]
    ClickFav2 --> CheckLogin2
    
    %% 路徑 B：個人中心管理
    Actions -->|2. 進入個人中心| Profile[個人首頁]
    Profile --> CheckLogin3{已登入？}
    CheckLogin3 -->|否| ToLogin
    CheckLogin3 -->|是| ProfileTabs{選擇查看分頁}
    
    ProfileTabs -->|我的收藏| FavPage[收藏清單 favorites.html]
    FavPage --> ClickCard[點擊餐廳卡片] --> ViewDetail
    FavPage --> ClickUnfav[點擊取消收藏] --> AJAXUnfav[AJAX 刪除] --> FadeCard[卡片漸隱移除]
    
    ProfileTabs -->|歷史紀錄| HistPage[歷史紀錄 history.html]
    HistPage --> ClickHistName[點擊餐廳名稱] --> ViewDetail
    HistPage --> QuickFav[點擊歷史列表愛心] --> AJAXToggleHist[AJAX 收藏/取消] --> UpdateHistUI[更新列表愛心]

    ToLogin --> LoginSuccess[登入成功] --> Home
```

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 收藏/取消收藏 (AJAX Toggle Flow)
此序列圖詳細描述使用者點擊收藏按鈕後，瀏覽器、Flask 後端與 SQLite 資料庫之間的非同步資料互動。

```mermaid
sequenceDiagram
    autonumber
    actor User as 使用者
    participant Browser as 瀏覽器 (detail.html / result.html)
    participant Flask as Flask Route (/favorite/toggle)
    participant Model as SQLAlchemy (Favorite Model)
    participant DB as SQLite 資料庫

    User->>Browser: 點擊「收藏/取消收藏」愛心按鈕
    Browser->>Flask: POST /favorite/toggle (攜帶 restaurant_id, CSRF Token)
    Note over Flask: 檢查 Session 中 user 是否已登入
    alt 未登入
        Flask-->>Browser: 回傳 JSON: { status: "unauthorized", message: "請先登入" }
        Browser->>User: 顯示登入提示彈窗，並引導至登入頁面
    else 已登入
        Flask->>Model: 查詢是否已有該 user_id 與 restaurant_id 的關聯
        Model->>DB: SELECT * FROM favorites WHERE user_id AND restaurant_id
        DB-->>Model: 回傳查詢結果
        
        alt 已經收藏 (記錄存在)
            Flask->>Model: 刪除收藏
            Model->>DB: DELETE FROM favorites WHERE id = :id
            DB-->>Flask: 成功刪除
            Flask-->>Browser: 回傳 JSON: { status: "success", favorited: false }
        else 尚未收藏 (記錄不存在)
            Flask->>Model: 新增收藏
            Model->>DB: INSERT INTO favorites (user_id, restaurant_id)
            DB-->>Flask: 成功寫入
            Flask-->>Browser: 回傳 JSON: { status: "success", favorited: true }
        end
        Browser->>User: 轉換愛心圖示 (❤️ / 🤍) 並彈出 Toast 成功提示
    end
```

### 2.2 隨機推薦並自動記錄歷史
當登入使用者點擊「抽！」時，系統如何將抽選結果與推薦歷史寫入資料庫：

```mermaid
sequenceDiagram
    autonumber
    actor User as 使用者 (已登入)
    participant Browser as 瀏覽器 (index.html)
    participant Flask as Flask Route (/spin)
    participant Model as SQLAlchemy (History Model)
    participant DB as SQLite 資料庫

    User->>Browser: 點擊「抽！」按鈕
    Browser->>Flask: POST /spin (帶入篩選條件)
    Note over Flask: 執行隨機篩選演算法，選出 restaurant_id
    
    alt 使用者已登入
        Flask->>Model: 建立歷史推薦記錄
        Model->>DB: INSERT INTO recommendation_histories (user_id, restaurant_id)
        DB-->>Flask: 成功寫入歷史
    end
    
    Flask-->>Browser: 重導向至 /restaurant/:id (或回傳結果)
    Browser->>User: 渲染抽選結果頁面，展示餐廳詳情
```

---

## 3. 功能清單對照表

本功能的路由配置與權限管理如下：

| 功能名稱 | URL 路徑 | HTTP 方法 | 登入防護 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| **隨機推薦** | `/spin` | `POST` | 否 | 提交篩選條件進行抽選。若使用者已登入，則自動寫入歷史紀錄。 |
| **收藏狀態切換** | `/favorite/toggle` | `POST` | 是 | 透過 AJAX POST 請求切換收藏/取消收藏狀態，避免網頁重載。 |
| **我的收藏清單** | `/profile/favorites` | `GET` | 是 | 進入個人中心，載入並渲染已收藏餐廳（Jinja2 渲染 `favorites.html`）。 |
| **歷史推薦紀錄** | `/profile/history` | `GET` | 是 | 進入個人中心，載入並渲染歷史推薦清單（Jinja2 渲染 `history.html`）。 |
