# 路由模組套件包初始化 (Routes Package Initialization)
# 為了在此設計階段維持本機開發伺服器的百分之百健康運作與測試功能，
# 我們在此將主運行 Blueprint (main_bp) 參照引導至已實作之 routes_monolith 模組中。

from app.routes_monolith import main_bp
