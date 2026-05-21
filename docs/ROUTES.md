# 隨便吃什麼都好系統 - 路由與頁面設計文件 (ROUTES.md)

本文件詳細規劃了「隨便吃什麼都好 (FlavorFind)」系統的 Flask 路由 (Routes)、對應的 HTTP 方法、輸入/輸出格式、Jinja2 前端模板結構，以及控制器的程式碼骨架架構。

---

## 1. 路由總覽表格

本系統採用質感 Single-page App (SPA-like) 架構，核心畫面主要在一個主視圖 (`index.html`) 中動態切換顯示，其他功能藉由非同步 RESTful APIs (AJAX Fetch) 與後端進行資料即時交互。

| 功能名稱 | HTTP 方法 | URL 路徑 | 對應 Jinja2 模板 | 說明 |
| --- | --- | --- | --- | --- |
| **主網頁頁面** | `GET` | `/` | `templates/index.html` | 系統入口點，載入三頁籤分頁（探索、口袋名單、探險日誌）的毛玻璃外觀與 JS。 |
| **一鍵抽籤推薦** | `POST` | `/api/recommend` | — (返回 JSON) | 接收經緯度、距離、預算與排除條件，隨機挑選餐廳並寫入抽籤紀錄。 |
| **查詢餐廳種類** | `GET` | `/api/categories` | — (返回 JSON) | 動態取得資料庫中不重複之分類標籤，供前端渲染防雷篩選區。 |
| **查詢口袋名單** | `GET` | `/api/favorites` | — (返回 JSON) | 獲取當前 Session 用戶收藏的全部口袋餐廳詳情列表。 |
| **切換收藏狀態** | `POST` | `/api/favorites/toggle`| — (返回 JSON) | 接收餐廳 ID，自動切換該餐廳於口袋名單中的收藏/取消收藏狀態。 |
| **新增自訂私房菜**| `POST` | `/api/restaurants/custom`| — (返回 JSON) | 接收使用者自訂的餐廳表單，寫入資料庫並自動加入收藏。 |
| **查詢歷史日誌** | `GET` | `/api/history` | — (返回 JSON) | 獲取當前 Session 用戶的所有美食探險紀錄（按時間降序）。 |
| **更新美食回饋** | `POST` | `/api/history/<id>/feedback`| — (返回 JSON) | 接收 1-5 星等評分與心得評語，更新特定推薦歷史紀錄。 |
| **刪除歷史紀錄** | `DELETE` | `/api/history/<id>` | — (返回 JSON) | 刪除單筆特定的推薦歷史項目。 |

*註：由於本系統全面使用非同步 Fetch API (AJAX) 進行互動，除了首頁路由外，其餘端點均為標準的 JSON API 介面，以提供無縫、無重新整理的原生 App 級操作感。*

---

## 2. 每個路由的詳細說明

### A. 首頁頁面路由 (`GET /`)
* **輸入**：無。
* **處理邏輯**：
  - 初始化或驗證 Flask `session`，若無 `session_id` 則自動為其產生隨機唯一的 UUID，寫入 Cookie 儲存。
  - 調用 Flask `render_template` 渲染主畫面外殼。
* **輸出**：渲染 `index.html`（繼承自 `base.html`）。
* **錯誤處理**：若連線或渲染失敗，回傳 `500 Internal Server Error`。

### B. 一鍵推薦 API (`POST /api/recommend`)
* **輸入**：
  - JSON Body：`lat` (Float, 可空), `lng` (Float, 可空), `budget` (Int), `distance` (Float), `min_rating` (Float), `categories_exclude` (List of String), `only_favorites` (Boolean)
* **處理邏輯**：
  - 呼叫 `restaurant.py` 中的 `recommend_restaurant` 進行篩選推薦。
  - 若推薦成功，呼叫 `history.py` 中的 `add_history` 寫入一筆探險歷史紀錄，並透過 `is_favorite` 判斷收藏狀態。
* **輸出**：
  - 成功：`200 OK`，JSON `{"success": true, "data": { 餐廳資料 }}`。
  - 失敗/無匹配：`404 Not Found`，JSON `{"success": false, "message": "錯誤訊息提示"}`。

### C. 分類標籤查詢 API (`GET /api/categories`)
* **輸入**：Session 中的 `session_id`。
* **處理邏輯**：
  - 查詢資料庫中 `is_custom = 0` (系統預設) 或 `session_id = ?` (該用戶自訂) 的不重複餐廳分類標籤。
* **輸出**：`200 OK`，JSON `{"success": true, "data": [ "分類1", "分類2" ]}`。

### D. 口袋名單查詢 API (`GET /api/favorites`)
* **輸入**：Session 中的 `session_id`。
* **處理邏輯**：
  - 呼叫 `favorite.py` 模型中的 `get_favorites(session_id)` 獲取該 Session 收藏的所有餐廳詳情。
* **輸出**：`200 OK`，JSON `{"success": true, "data": [ 收藏餐廳清單 ]}`。

### E. 收藏切換 API (`POST /api/favorites/toggle`)
* **輸入**：JSON Body 中的 `restaurant_id` (Int, 必填)。
* **處理邏輯**：
  - 驗證 `restaurant_id` 欄位。
  - 呼叫 `is_favorite` 檢查是否已收藏。若是則調用 `remove_favorite` 取消收藏，若否則調用 `add_favorite` 加入收藏。
* **輸出**：`200 OK`，JSON `{"success": true, "is_favorite": Boolean}`。
* **錯誤處理**：若 ID 缺失回傳 `400 Bad Request`；其餘異常回傳 `500 Internal Server Error`。

### F. 新增私房菜 API (`POST /api/restaurants/custom`)
* **輸入**：
  - JSON Body：`name` (String, 必填), `category` (String, 必填), `budget_level` (Int), `google_maps_url` (String, 可選)
* **處理邏輯**：
  - 驗證 `name` 和 `category` 欄位防空。
  - 呼叫 `add_custom_restaurant` 將其存入餐廳庫並標記為自訂私房菜。
  - **決策優化**：新增成功後，自動呼叫 `add_favorite` 將該私房餐廳加入此 Session 的收藏口袋名單中。
* **輸出**：`200 OK`，JSON `{"success": true, "message": "提示文字", "data": { 餐廳極簡資料 }}`。
* **錯誤處理**：欄位缺失回傳 `400 Bad Request`；資料庫寫入異常回傳 `500`。

### G. 歷史探險日誌 API (`GET /api/history`)
* **輸入**：Session 中的 `session_id`。
* **處理邏輯**：
  - 呼叫 `history.py` 中的 `get_history(session_id)`，按推薦生成時間降序讀取歷史紀錄。
* **輸出**：`200 OK`，JSON `{"success": true, "data": [ 歷史日誌清單 ]}`。

### H. 美食評價回饋 API (`POST /api/history/<int:history_id>/feedback`)
* **輸入**：
  - URL Parameter：`history_id` (Int)
  - JSON Body：`user_rating` (Int, 1-5 星), `comment` (String)
* **處理邏輯**：
  - 驗證星級評分必須為 1 到 5 之間。
  - 呼叫 `update_history_feedback` 更新資料庫對應之評語與分數。
* **輸出**：`200 OK`，JSON `{"success": true, "message": "感謝您的真實心得回饋！"}`。
* **錯誤處理**：評分不合法回傳 `400`；項目不屬於該用戶或不存在回傳 `404`。

### I. 刪除歷史紀錄 API (`DELETE /api/history/<int:history_id>`)
* **輸入**：URL Parameter：`history_id` (Int)。
* **處理邏輯**：
  - 呼叫 `delete_history(session_id, history_id)` 從 SQLite 中移除對應紀錄。
* **輸出**：`200 OK`，JSON `{"success": true, "message": "已刪除該條推薦歷史！"}`。
* **錯誤處理**：不存在或無權限回傳 `404`。

---

## 3. Jinja2 模板清單

前端視圖模組儲存於 `app/templates/` 中，保持簡潔乾淨的階層關係：

1. **`templates/base.html`** (基礎主要模板)
   - **職責**：提供整個系統共享的 HTML5 骨架結構。
   - **載入資源**：
     - Google Fonts (`Inter`, `Noto Sans TC`) 提供優雅現代的字型。
     - Bootstrap 5 CSS & JS (提供響應式基礎格線與組件結構)。
     - Bootstrap Icons CDN (提供地圖、心形、垃圾桶、指南針等質感圖示)。
   - **定義區塊**：定義 `{% block content %}{% endblock %}` 供子視圖嵌入。

2. **`templates/index.html`** (首頁主模板，繼承自 `base.html`)
   - **職責**：實作單頁 App 外殼與 Glassmorphism 毛玻璃容器。
   - **包含區塊**：
     - **探索 (Explore) 容器**：手動地標下拉選單、預算/距離滑桿、進階防雷篩選標籤區、Recommend 按鈕、滾輪抽籤 Slot Machine 動畫遮罩、推薦結果卡片。
     - **口袋名單 (Favorites) 容器**：口袋名單列表、自訂私房菜表單。
     - **探險日誌 (Journal) 容器**：歷史紀錄卡片清單、1-5 星星互動評分、心得文字輸入區。
     - **底部導覽列 (Bottom Nav Bar)**：實現三個分頁 Tabs 之間無重新整理切換的毛玻璃控制鈕。

---

## 4. 路由骨架程式碼

以下展示控制器層 (Controller/Routes) 的 Python 檔案骨架定義與 docstring：

### A. 主網頁控制器骨架 ([app/routes/main.py](file:///Users/huihsin/very-good-1/app/routes/main.py))
```python
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    渲染 FlavorFind 首頁入口視圖。
    
    Returns:
        HTML: 渲染後的 index.html 頁面，自動包含三頁籤 Tabs 架構。
    """
    pass
```

### B. RESTful API 控制器骨架 ([app/routes/api.py](file:///Users/huihsin/very-good-1/app/routes/api.py))
```python
from flask import Blueprint, request, jsonify, session

api_bp = Blueprint('api', __name__, url_prefix='/api')

def init_session():
    """
    輔助函式：初始化 Flask Session。
    當用戶首次進入時，自動為其生成一個唯一的 UUID 存入 cookie，以實現隱私的無感數據隔離。
    """
    pass

@api_bp.route('/recommend', methods=['POST'])
def recommend():
    """
    一鍵抽籤推薦 API。
    接收前端提供的經緯度及過濾條件，呼叫推薦算法挑選最合適之餐館，寫入歷史日誌並回傳。
    
    Payload:
        lat (float, optional)
        lng (float, optional)
        budget (int)
        distance (float)
        min_rating (float)
        categories_exclude (list)
        only_favorites (bool)
        
    Returns:
        JSON: 包含餐廳資訊及 is_favorite 狀態。
    """
    pass

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    獲取當前可見之所有不重複分類標籤 API。
    包含系統預設分類與當前 Session 用戶自訂私房菜分類。
    
    Returns:
        JSON: 包含分類字串陣列。
    """
    pass

@api_bp.route('/favorites', methods=['GET'])
def list_favorites():
    """
    獲取當前 Session 用戶的所有收藏口袋名單詳情列表。
    
    Returns:
        JSON: 餐廳詳情清單。
    """
    pass

@api_bp.route('/favorites/toggle', methods=['POST'])
def toggle_favorite():
    """
    非同步切換指定餐廳收藏狀態 API。
    
    Payload:
        restaurant_id (int)
        
    Returns:
        JSON: 最新之 is_favorite (bool) 收藏狀態。
    """
    pass

@api_bp.route('/restaurants/custom', methods=['POST'])
def create_custom_restaurant():
    """
    新增自訂私房餐廳 API。
    驗證欄位完整後，寫入資料庫主表並自動對其進行收藏。
    
    Payload:
        name (str)
        category (str)
        budget_level (int)
        google_maps_url (str, optional)
        
    Returns:
        JSON: 成功狀態及新餐廳資訊。
    """
    pass

@api_bp.route('/history', methods=['GET'])
def list_history():
    """
    獲取當前 Session 用戶的推薦抽籤歷史紀錄 API。
    依時間由新到舊排列。
    
    Returns:
        JSON: 歷史紀錄日誌列表。
    """
    pass

@api_bp.route('/history/<int:history_id>/feedback', methods=['POST'])
def save_feedback(history_id):
    """
    對特定的歷史推薦紀錄給予星級評分與文字心得 API。
    
    Payload:
        user_rating (int) - 1-5 的整數星等
        comment (str) - 心得感想短評
        
    Returns:
        JSON: 成功儲存提示訊息。
    """
    pass

@api_bp.route('/history/<int:history_id>', methods=['DELETE'])
def delete_history_entry(history_id):
    """
    刪除特定一筆歷史推薦紀錄 API。
    
    Returns:
        JSON: 成功刪除提示。
    """
    pass
```
