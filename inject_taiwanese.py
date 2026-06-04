from app import create_app, db
from app.models.restaurant import Restaurant
import random

def inject_real_taiwanese_food():
    app = create_app()
    with app.app_context():
        # User requested specific places and real Taichung/Fengchia street food
        places = [
            "紅豆食堂", "傻瓜麵", "明倫蛋餅", "日船章魚小丸子", "官芝霖大腸包小腸",
            "激旨燒鳥", "逢甲溫家地瓜球", "一心素食臭豆腐", "大甲芋頭城", "炳叔烤玉米",
            "海邊小屋", "黃金右腿", "黃金左腿", "豬寶盒", "熊手包",
            "逢甲四合一", "帝鈞胡椒餅", "惡魔雞排", "按摩雞排", "逢甲冰火菠蘿油",
            "財神爺滷肉飯", "豐原廟東清水排骨麵", "阿華黑輪", "黑肉麵", "尊品原汁牛肉麵",
            "逢甲炒餅條", "陳媽媽台灣小吃", "逢甲廟口鹽酥雞", "小寶河南蔥花大餅", "成記手工麵線",
            "台中肉員", "茂川肉丸", "丁山肉丸", "老賴紅茶", "王記菜頭粿糯米腸",
            "山河魯肉飯", "李海魯肉飯", "科博館水煎包", "天天饅頭", "中華路夜市蚵仔煎",
            "東泉辣椒醬炒麵", "大麵羹老店", "麻豆碗粿", "台南擔仔麵逢甲店", "阿財米糕",
            "清水排骨酥麵", "正老牌香菇肉羹", "旱溪夜市排隊地瓜球", "忠孝夜市烤肉", "旱溪炒麵"
        ]
        
        added = 0
        for name in places:
            # Check if exists
            if not Restaurant.query.filter_by(name=name).first():
                lat_offset = random.uniform(-0.05, 0.05)
                lng_offset = random.uniform(-0.05, 0.05)
                
                res = Restaurant(
                    name=name,
                    category="台式", # Specifically using '台式' so it appears in the filter
                    rating=round(random.uniform(4.0, 4.9), 1),
                    address="台中市逢甲周邊與知名夜市",
                    price_level=1, # 平價 (200元內)
                    distance=random.randint(100, 8000),
                    lat=24.180 + lat_offset,
                    lng=120.648 + lng_offset
                )
                db.session.add(res)
                added += 1
                
        db.session.commit()
        print(f"成功新增 {added} 家正宗「台式」平價小吃與路邊攤！")

if __name__ == '__main__':
    inject_real_taiwanese_food()
