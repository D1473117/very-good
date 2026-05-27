# 路由設計 - 收藏與歷史紀錄功能 (F-05)

## 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| 收藏列表 | GET | `/favorites` | `favorites.html` | 顯示所有收藏的餐廳 |
| 新增收藏 | POST | `/favorites/add` | — | 接收表單，將餐廳加入收藏，完成後重導向至列表 |
| 刪除收藏 | POST | `/favorites/delete/<id>` | — | 刪除指定的收藏餐廳，完成後重導向至列表 |
| 歷史紀錄列表 | GET | `/history` | `history.html` | 顯示所有推薦的歷史紀錄 |
| 新增歷史紀錄 | POST | `/history/add` | — | 接收表單，將餐廳加入歷史紀錄，完成後重導向或繼續流程 |

## 每個路由的詳細說明

### 1. `/favorites` (GET)
* **輸入**: 無
* **處理邏輯**: 呼叫 `Favorite.get_all()` 取得所有收藏
* **輸出**: 渲染 `favorites.html`，並將取得的資料傳遞給模板
* **錯誤處理**: 若無資料則顯示空狀態提示

### 2. `/favorites/add` (POST)
* **輸入**: 表單欄位 (restaurant_name, category, rating, address)
* **處理邏輯**: 驗證必填欄位 `restaurant_name`，然後呼叫 `Favorite.create(data)`
* **輸出**: 成功後重導向至 `/favorites` (或原本的推薦頁面)，使用 flash 顯示成功訊息
* **錯誤處理**: 資料驗證失敗時，使用 flash 顯示錯誤訊息，並返回上一頁

### 3. `/favorites/delete/<id>` (POST)
* **輸入**: URL 參數 `id`
* **處理邏輯**: 呼叫 `Favorite.delete(id)` 進行刪除
* **輸出**: 成功後重導向至 `/favorites`，使用 flash 顯示成功訊息
* **錯誤處理**: 若 ID 不存在，或刪除失敗，flash 錯誤訊息並重導向

### 4. `/history` (GET)
* **輸入**: 無
* **處理邏輯**: 呼叫 `History.get_all()` 取得所有歷史紀錄
* **輸出**: 渲染 `history.html`，並將取得的資料傳遞給模板
* **錯誤處理**: 若無資料則顯示空狀態提示

### 5. `/history/add` (POST)
* **輸入**: 表單欄位 (restaurant_name, category, rating)
* **處理邏輯**: 驗證必填欄位 `restaurant_name`，然後呼叫 `History.create(data)`
* **輸出**: 成功後依流程重導向
* **錯誤處理**: 若寫入失敗，使用 flash 或回傳錯誤狀態碼

## Jinja2 模板清單

* `favorites.html`: 繼承 `base.html`，包含呈現收藏餐廳的清單與刪除用的 POST 表單。
* `history.html`: 繼承 `base.html`，包含呈現歷史紀錄的清單。
