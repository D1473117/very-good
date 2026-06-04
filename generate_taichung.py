import random
from app import create_app, db
from app.models.restaurant import Restaurant

def generate_taichung_restaurants():
    app = create_app()
    with app.app_context():
        prefixes = ['逢甲', '一中', '東海', '公益路', '七期', '北屯', '西區', '南屯', '水湳', '草悟道']
        adjectives = ['阿伯', '無名', '老牌', '正宗', '超人氣', '排隊', '隱藏版', '巷口', '必吃', '傳奇', '阿嬤的', '道地', '金牌', '手工', '極品']
        food_types = ['拉麵', '滷肉飯', '牛肉麵', '火鍋', '燒肉', '早午餐', '咖哩', '義大利麵', '雞排', '手搖飲', '甜點', '居酒屋', '鐵板燒', '壽司', '便當', '水餃', '炒麵', '爌肉飯', '鹽酥雞']
        
        generated = set()
        added_count = 0
        
        while added_count < 500:
            p = random.choice(prefixes)
            a = random.choice(adjectives)
            f = random.choice(food_types)
            
            patterns = [
                f"{p}{a}{f}",
                f"{p}{f}名店",
                f"{a}{f} - {p}店",
                f"{p}特製{f}",
                f"大台中{a}{f}"
            ]
            
            name = random.choice(patterns)
            
            if name not in generated and not Restaurant.query.filter_by(name=name).first():
                generated.add(name)
                
                price = random.choice([1, 1, 2, 2, 2, 3, 3, 4])
                rating = round(random.uniform(3.5, 4.9), 1)
                
                lat_offset = random.uniform(-0.09, 0.09)
                lng_offset = random.uniform(-0.09, 0.09)
                
                res = Restaurant(
                    name=name,
                    category=f,
                    rating=rating,
                    address=f"台中市{p}商圈附近",
                    price_level=price,
                    distance=random.randint(50, 10000),
                    lat=24.180 + lat_offset,
                    lng=120.648 + lng_offset
                )
                db.session.add(res)
                added_count += 1
                
        db.session.commit()
        print(f"成功注入 {added_count} 家「逢甲10公里內」的全新打卡餐廳！現在資料庫超級豐富！")

if __name__ == '__main__':
    generate_taichung_restaurants()
