# 路由設計文件（ROUTES）- F-05 收藏與歷史紀錄

**專案名稱：** 隨便吃什麼都好（Let's Just Eat）  
**功能模組：** F-05 收藏與歷史紀錄 (Favorites & History)  
**對應 DB 設計：** [docs/DB_DESIGN.md](file:///c:/Users/USER/very-good/docs/DB_DESIGN.md)  
**Blueprint 前綴：**  
- 收藏：`favorite_bp`（無 URL prefix）  
- 歷史：`history_bp`（無 URL prefix）  
**撰寫日期：** 2026-05-27  

---

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 收藏清單 | GET | `/favorites` | `profile/favorites.html` | 顯示所有收藏餐廳卡片 |
| 新增收藏 | POST | `/favorites/add` | — | 接收表單，存入 DB，重導向至 `/favorites` |
| 刪除收藏 | POST | `/favorites/delete/<id>` | — | 依 ID 刪除收藏，重導向至 `/favorites` |
| 歷史紀錄清單 | GET | `/history` | `profile/history.html` | 顯示推薦歷史清單（含分頁） |
| 新增歷史紀錄 | POST | `/history/add` | — | 系統抽選後自動呼叫，存入 DB，重導向至抽選結果頁 |

---

## 2. 每個路由的詳細說明

### 2.1 `GET /favorites` — 收藏清單頁

| 項目 | 說明 |
| :--- | :--- |
| **輸入** | 無（從 Session 取得當前使用者）|
| **處理邏輯** | 呼叫 `Favorite.get_all()` 取得所有收藏，依 `created_at` 降序 |
| **輸出** | 渲染 `profile/favorites.html`，傳入 `favorites` 清單 |
| **錯誤處理** | Model 回傳空清單時，模板顯示「尚無收藏」的 Empty State |
| **登入防護** | `@login_required` |

---

### 2.2 `POST /favorites/add` — 新增收藏

| 項目 | 說明 |
| :--- | :--- |
| **輸入（表單欄位）** | `restaurant_name`（必填）、`category`、`rating`、`address` |
| **處理邏輯** | 驗證 `restaurant_name` 不為空 → 呼叫 `Favorite.create(...)` |
| **輸出（成功）** | `flash('成功加入收藏！', 'success')` → `redirect('/favorites')` |
| **輸出（失敗）** | `flash('餐廳名稱不可為空', 'warning')` → `redirect(request.referrer)` |
| **錯誤處理** | Model 回傳 None 時顯示系統錯誤 flash |
| **登入防護** | `@login_required` |

---

### 2.3 `POST /favorites/delete/<id>` — 刪除收藏

| 項目 | 說明 |
| :--- | :--- |
| **輸入（URL 參數）** | `id`（整數，收藏紀錄主鍵） |
| **處理邏輯** | 呼叫 `Favorite.delete(id)` |
| **輸出（成功）** | `flash('已從收藏移除', 'success')` → `redirect('/favorites')` |
| **輸出（找不到）** | `flash('找不到此收藏紀錄', 'warning')` → `redirect('/favorites')` |
| **錯誤處理** | `id` 非整數時回傳 404 |
| **登入防護** | `@login_required` |

---

### 2.4 `GET /history` — 歷史紀錄列表頁

| 項目 | 說明 |
| :--- | :--- |
| **輸入（URL 參數）** | `page`（選填，預設為 1） |
| **處理邏輯** | 計算 `offset = (page-1) * 10`，呼叫 `History.get_all(limit=10, offset=offset)` |
| **輸出** | 渲染 `profile/history.html`，傳入 `histories`、`page`、`total_pages` |
| **錯誤處理** | 歷史清單為空時模板顯示 Empty State |
| **登入防護** | `@login_required` |

---

### 2.5 `POST /history/add` — 新增歷史紀錄（系統呼叫）

| 項目 | 說明 |
| :--- | :--- |
| **輸入（表單欄位）** | `restaurant_name`（必填）、`category`、`rating` |
| **處理邏輯** | 由抽選路由（`/spin`）完成推薦後內部呼叫，呼叫 `History.create(...)` |
| **輸出（成功）** | `redirect` 至抽選結果頁面 |
| **輸出（失敗）** | `flash('歷史紀錄寫入失敗', 'warning')` |
| **錯誤處理** | Model 回傳 None 時顯示 flash 警告，不中斷主流程 |
| **登入防護** | `@login_required` |

---

## 3. Jinja2 模板清單

| 模板路徑 | 繼承自 | 說明 |
| :--- | :--- | :--- |
| `app/templates/base.html` | — | 共用版型（Navbar、Flash messages、Footer） |
| `app/templates/profile/favorites.html` | `base.html` | 收藏清單頁，Bootstrap 5 卡片佈局 |
| `app/templates/profile/history.html` | `base.html` | 歷史紀錄列表頁，Bootstrap 5 表格 + 分頁 |

---

## 4. Blueprint 註冊方式

在 `app/__init__.py` 的 `create_app()` 工廠函數中加入：

```python
from app.routes.favorite_routes import favorite_bp
from app.routes.history_routes import history_bp

app.register_blueprint(favorite_bp)
app.register_blueprint(history_bp)
```
