# 隨便吃什麼都好系統 - 流程圖文件 (Flowchart)

本文件根據 PRD 需求與系統架構設計，視覺化呈現使用者的操作路徑以及系統內部的資料流動。

## 1. 使用者流程圖 (User Flow)

此流程圖描述了使用者進入平台後，如何操作單人推薦、群組決策模式，以及管理個人設定（口袋名單、避雷針與歷史紀錄）。

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B[首頁/單人隨機推薦]
    B --> C{選擇功能模式}
    C -->|單人模式| D[設定預算、距離等條件]
    D --> E[點擊一鍵抽籤]
    E --> F[顯示餐廳結果與導航]
    
    C -->|群組模式| G[建立或輸入代碼加入群組]
    G --> H[進入群組大廳]
    H --> I[所有成員準備後開始轉盤]
    I --> J[顯示群組共識結果]
    
    C -->|個人中心| K[進入個人頁面]
    K --> L{管理選項}
    L -->|口袋名單| M[新增/刪除專屬餐廳]
    L -->|飲食避雷針| N[設定過敏或拒吃類型]
    L -->|探險紀錄| O[查看歷史抽籤紀錄並給予評價]
```

## 2. 系統序列圖 (Sequence Diagram)

以下以「單人隨機推薦 (一鍵抽籤)」為例，展示從使用者點擊按鈕到看見結果的系統內部運作流程。

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route (Controller)
    participant Model as Database Model
    participant DB as SQLite

    User->>Browser: 勾選條件並點擊「隨機推薦」
    Browser->>Route: POST /recommend (帶入篩選參數)
    Route->>Model: 呼叫 get_random_restaurant(條件, 避雷設定)
    Model->>DB: 執行 SQL (WHERE 符合條件 ORDER BY RANDOM LIMIT 1)
    DB-->>Model: 回傳單筆餐廳資料
    Model-->>Route: 餐廳物件資料
    Route->>Route: 將資料帶入 Jinja2 渲染 result.html
    Route-->>Browser: 回傳渲染後的 HTML 頁面
    Browser-->>User: 顯示推薦餐廳與相關資訊
```

## 3. 功能清單對照表

本表格將 PRD 中規劃的功能對應至預計實作的 URL 路徑與 HTTP 方法，供後續開發 Route 參考。

| 功能名稱 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :--- | :--- |
| **首頁 / 單人條件設定** | `/` | GET | 顯示首頁表單，讓使用者輸入單人抽籤的條件 |
| **執行單人推薦** | `/recommend` | POST | 接收首頁表單條件，進行隨機抽取並顯示結果頁面 |
| **建立群組決策** | `/group/create` | POST | 產生一個新的群組房間，並回傳邀請連結/代碼 |
| **群組大廳** | `/group/<room_id>` | GET | 顯示群組內的成員狀態與轉盤介面 |
| **群組執行抽取** | `/group/<room_id>/spin`| POST | 執行群組共識的隨機抽取，並更新群組結果 |
| **個人設定頁面** | `/profile` | GET | 顯示口袋名單、避雷針與歷史紀錄的入口 |
| **新增/編輯口袋名單** | `/profile/restaurants` | POST | 將新的餐廳加入使用者的專屬名單 |
| **更新飲食避雷針** | `/profile/blacklist` | POST | 更新使用者不想吃的分類或過敏源設定 |
| **新增歷史評價** | `/history/rate` | POST | 針對過去抽到的餐廳填寫簡單評價與分數 |
