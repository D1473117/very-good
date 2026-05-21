# 餐廳資訊顯示 - 架構與介面設計

這份文件針對「餐廳資訊顯示」功能（負責顯示餐廳名稱、地址、評分、營業時間等資訊）進行了資料庫結構與 UI/UX 流程的規劃。

## 1. 資料庫結構規劃 (Database Schema)

因為這項功能主要負責「呈現餐廳資訊」，我們需要一個 `Restaurant` 資料表來儲存這些欄位。如果後續串接 Google Places API，我們也可以將取得的結果快取到這個資料表中以提升效能並減少 API 呼叫次數。

```mermaid
erDiagram
    Restaurant {
        INTEGER id PK "主鍵"
        STRING place_id "Google Places API 的唯一 ID"
        STRING name "餐廳名稱"
        STRING address "完整地址"
        FLOAT rating "評分 (0.0 - 5.0)"
        INTEGER user_ratings_total "評分總人數"
        STRING open_hours "營業時間 (JSON 或字串格式)"
        STRING photo_url "餐廳照片 URL"
        FLOAT latitude "緯度"
        FLOAT longitude "經度"
        INTEGER price_level "價格區間 (1-4)"
        STRING category "餐點類型"
        STRING signature "招牌美味必點"
    }
```

## 2. 系統架構與 UI/UX 流程 (Architecture & Flow)

當使用者點擊「隨機推薦」後，系統的處理流程與 UI 互動如下：

```mermaid
sequenceDiagram
    participant U as 使用者 (Frontend)
    participant F as 前端介面 (HTML/JS)
    participant B as 後端伺服器 (Flask)
    participant DB as 資料庫 (SQLite)
    participant API as Google Places API

    U->>F: 點擊「一鍵隨機推薦」按鈕
    F->>B: 發送推薦請求 (帶有經緯度或篩選條件)
    
    alt 優先從本地資料庫尋找
        B->>DB: 查詢符合條件的餐廳
        DB-->>B: 回傳餐廳清單
    else 資料庫無資料或需更新
        B->>API: 呼叫 Google Places API 搜尋附近餐廳
        API-->>B: 回傳餐廳資料 (包含 place_id)
        B->>API: 透過 place_id 取得詳細資訊 (營業時間、照片等)
        API-->>B: 回傳詳細資訊
        B->>DB: 將新餐廳資料存入資料庫快取
    end
    
    B->>B: 執行隨機抽取演算法
    B-->>F: 回傳單一餐廳詳細資訊 (JSON)
    F->>U: 渲染餐廳結果卡片 (名稱、地址、評分、營業時間)
    
    opt 使用者後續操作
        U->>F: 點擊「查看地圖」
        F->>U: 開啟 Google Maps 導航連結
    end
```

## 3. 介面設計 (UI/UX Mockup)

請參考系統生成的 Mockup 預覽圖。介面設計重點如下：
- **視覺焦點**：頂部為大面積的餐廳美食照片，吸引食慾。
- **資訊層級**：以粗大字體顯示「餐廳名稱」，緊接著是「評分（星號）」、「營業時間」與「地址」。
- **行動呼籲 (CTA)**：
  - 主要按鈕（Primary Button）：**「導航去吃」**(Get Directions)，使用亮色系，點擊後開啟地圖。
  - 次要按鈕（Secondary Button）：**「再抽一次」**(Draw Again)，讓使用者快速重新選擇。
- **風格設計**：採用 RWD 與 Glassmorphism（毛玻璃）風格，圓角卡片設計，確保手機與桌面版都有良好的閱讀體驗。

![Restaurant Info Mockup](C:\Users\AmyLin\.gemini\antigravity\brain\720db8b8-b4cd-4193-9898-d0a3b32c6518\restaurant_info_mockup_1778722274592.png)
