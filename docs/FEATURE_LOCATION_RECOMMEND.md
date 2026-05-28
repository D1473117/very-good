# 附近餐廳推薦 - 系統架構與介面設計

這份文件專注於「系統可取得使用者目前位置，並推薦附近餐廳」這項核心功能的架構與介面規劃。

## 1. 系統架構與元件關係 (Architecture)

### 元件架構圖
使用 Flask MVC 架構，透過前端 JavaScript 取得裝置 GPS 位置，再將經緯度發送給後端，由後端呼叫 Google Places API 進行搜尋與推薦。

```mermaid
graph LR
    A[使用者瀏覽器] -->|1. 點擊定位/授權GPS| B(前端 HTML/JS)
    B -->|2. GET /recommend?lat=...&lng=...| C[Flask Route (Controller)]
    C -->|3. 查詢歷史紀錄| D[(SQLite Database)]
    C -->|4. 呼叫外部服務| E[Google Places API]
    E -->|5. 回傳餐廳清單| C
    D -->|回傳資料| C
    C -->|6. 隨機演算法挑選| C
    C -->|7. 渲染 Jinja2| B
    B -->|8. 顯示推薦結果| A
```

## 2. UI/UX 流程設計 (Flowchart)

### 使用者操作流程 (User Flow)
```mermaid
flowchart TD
    A([進入首頁]) --> B{是否授權定位？}
    B -- 否 --> C[手動輸入區域或地標]
    B -- 是 --> D[自動取得經緯度]
    C --> E[設定篩選條件<br>預算、距離、類型]
    D --> E
    E --> F[點擊「一鍵推薦」]
    F --> G{系統處理中...}
    G --> H[顯示單一推薦餐廳結果<br>含評分與地圖連結]
    H --> I{滿意嗎？}
    I -- 滿意 --> J([點擊地圖連結，出發用餐])
    I -- 不滿意 --> F
```

## 3. 資料庫結構規劃 (DB Design)

針對本功能，主要需要記錄使用者的「探險歷史」（曾經抽中過哪些餐廳），一方面能作為個人回顧，另一方面也可讓隨機演算法避免短期內重複推薦同一家餐廳。

### ER 圖
```mermaid
erDiagram
    RECOMMENDATION_HISTORY {
        int id PK
        string session_id "用戶識別碼"
        string restaurant_name "餐廳名稱"
        string place_id "Google Place ID"
        float lat "緯度"
        float lng "經度"
        datetime created_at "推薦時間"
    }
```

### 資料表說明
- **`recommendation_history`**（推薦歷史紀錄表）
    - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
    - `session_id`: `TEXT` (未強制登入時，可透過 Cookie 紀錄 Session ID 來辨識使用者)
    - `restaurant_name`: `TEXT` (餐廳名稱，直接存文字方便快速顯示)
    - `place_id`: `TEXT` (對應 Google Places API 的唯一識別碼，需要地圖連結時可直接帶入)
    - `lat` / `lng`: `REAL` (餐廳經緯度)
    - `created_at`: `DATETIME DEFAULT CURRENT_TIMESTAMP` (紀錄推薦產生的時間)

## 4. Mockup 介面預覽圖

以下為「附近餐廳推薦」的 UI 概念設計。採用現代感 Glassmorphism（毛玻璃）風格，主畫面清晰展示「定位地圖」、「條件滑桿（預算、距離）」以及醒目的「Recommend Nearby Food」一鍵推薦按鈕。

![附近餐廳推薦 Mockup](/Users/huihsin/.gemini/antigravity/brain/8fc08373-9b34-4f30-839e-de8f8aefd449/nearby_food_mockup_1778722056675.png)

---

## 5. 開發核心指導原則 (Core Developer Guidelines)

> [!IMPORTANT]
> **本專案的核心指令與首要功能為：「系統可取得使用者目前位置，並推薦附近餐廳」。**
> 後續進行任何代碼修改、重構或功能擴充時，必須嚴格遵守以下開發原則：

### A. 定位機制與防錯優先
1. **GPS 優先原則**：前端必須優先調用瀏覽器的 HTML5 Geolocation API。若 GPS 成功取得位置，必須即時更新畫面，並將最新的經緯度作為 API 請求的坐標。
2. **手動地標備用 (Fallback)**：必須提供預設地標選單（例如台北、逢甲等核心商圈）。若使用者拒絕 GPS 權限或定位失敗，手動選擇的地標坐標將作為基準。
3. **無縫預設值**：若 GPS 失敗且使用者未作任何選擇，系統後端必須以台北大安市中心坐標 `(25.041, 121.536)` 作為預設參考點，確保推薦功能 100% 能夠流暢執行，絕不可報錯。

### B. 推薦與距離計算演算法
1. **Haversine 距離公式**：後端必須使用標準的 Haversine 經緯度計算地球兩點直線距離。
2. **台灣道路常數係數 (1.4)**：由於直線距離比道路實際距離短，為符合台灣市區交通實況，必須將直線距離乘以 `1.4` 作為最終預估騎車距離，用以比對使用者的最大距離限制。
3. **Fallback 降級機制**：若套用距離過濾後沒有任何匹配的餐廳，推薦引擎必須自動降級（Fallback），即退回沒有距離限制的條件篩選集合中進行隨機抽取，確保系統絕不對使用者顯示「找不到符合條件的餐廳」死胡同。

### C. 抽籤歷史與防重複
1. 每次推薦成功的餐廳資訊（包含餐廳 ID、名稱、坐標及 Session ID）必須立即被寫入 `recommendation_history` 歷史表，作為日後美食日誌與星級回饋的基礎。
