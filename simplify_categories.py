from app import create_app, db
from app.models.restaurant import Restaurant
import random

def simplify_and_expand_restaurants():
    app = create_app()
    with app.app_context():
        # 1. 簡化現有分類
        restaurants = Restaurant.query.all()
        
        category_map = {
            '拉麵': '日式料理', '壽司': '日式料理', '居酒屋': '日式料理', '日式': '日式料理', '日式料理': '日式料理',
            '滷肉飯': '台式料理', '牛肉麵': '台式料理', '麵食': '台式料理', '水餃': '台式料理', '炒麵': '台式料理', 
            '爌肉飯': '台式料理', '便當': '台式料理', '中式': '台式料理', '中式料理': '台式料理', '台式': '台式料理', '台灣小吃': '台式料理',
            '義大利麵': '西式料理', '早午餐': '西式料理', '漢堡': '西式料理', '披薩': '西式料理', '西式': '西式料理',
            '火鍋': '鍋物燒烤', '燒肉': '鍋物燒烤', '鐵板燒': '鍋物燒烤',
            '雞排': '點心宵夜', '手搖飲': '點心宵夜', '甜點': '點心宵夜', '鹽酥雞': '點心宵夜', '咖啡廳': '點心宵夜', '小吃': '點心宵夜',
            '咖哩': '異國料理', '韓式料理': '異國料理', '綜合料理': '台式料理'
        }
        
        updated_count = 0
        for r in restaurants:
            old_cat = r.category
            new_cat = category_map.get(old_cat, '台式料理') # default to Taiwanese if unknown
            if old_cat != new_cat:
                r.category = new_cat
                updated_count += 1
                
        # 2. 大量新增更密集的周邊餐廳 (距離近，容易在「附近」找到)
        prefixes = ['逢甲', '河南路', '西屯', '福星路', '青海路', '秋紅谷', '逢甲大學', '文華路', '七期']
        adjectives = ['阿伯', '無名', '老牌', '正宗', '超人氣', '排隊', '隱藏版', '巷口', '必吃', '傳奇', '道地', '手工', '極品']
        broad_cats = ['台式料理', '日式料理', '西式料理', '異國料理', '鍋物燒烤', '點心宵夜']
        
        generated = set([r.name for r in restaurants])
        added_count = 0
        
        # Add 1500 new restaurants clustered very closely around Fengchia
        while added_count < 1500:
            p = random.choice(prefixes)
            a = random.choice(adjectives)
            c = random.choice(broad_cats)
            
            # Map category back to a random food type for naming
            food_name = "美食"
            if c == '台式料理': food_name = random.choice(['爌肉飯', '滷肉飯', '麵食館', '水餃', '牛肉麵'])
            elif c == '日式料理': food_name = random.choice(['拉麵', '壽司', '丼飯', '居酒屋'])
            elif c == '西式料理': food_name = random.choice(['義大利麵', '早午餐', '牛排', '餐酒館'])
            elif c == '鍋物燒烤': food_name = random.choice(['火鍋', '麻辣鍋', '燒肉', '串燒'])
            elif c == '點心宵夜': food_name = random.choice(['鹽酥雞', '串烤', '豆花', '冰品', '手搖飲'])
            elif c == '異國料理': food_name = random.choice(['咖哩', '泰式', '韓式烤肉', '越式河粉'])
            
            patterns = [
                f"{p}{a}{food_name}",
                f"{p}{food_name}名店",
                f"{a}{food_name} - {p}店",
                f"{p}特製{food_name}"
            ]
            
            name = random.choice(patterns)
            
            if name not in generated:
                generated.add(name)
                
                # Biased towards cheaper prices
                price = random.choice([1, 1, 1, 2, 2, 2, 3, 4])
                rating = round(random.uniform(3.5, 4.9), 1)
                
                # Extremely close distances for "Nearby" filter (50m ~ 3000m)
                distance = random.randint(50, 3000)
                
                res = Restaurant(
                    name=name,
                    category=c,
                    rating=rating,
                    address=f"台中市{p}周邊",
                    price_level=price,
                    distance=distance,
                    lat=24.180 + random.uniform(-0.02, 0.02),
                    lng=120.648 + random.uniform(-0.02, 0.02)
                )
                db.session.add(res)
                added_count += 1
                
        db.session.commit()
        print(f"成功將 {updated_count} 家現有餐廳重新分類！")
        print(f"成功新增 {added_count} 家「距離超近」的周邊美食！")

if __name__ == '__main__':
    simplify_and_expand_restaurants()
