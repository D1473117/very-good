from app import create_app, db
from app.models.restaurant import Restaurant
import os

app = create_app()

def seed_database():
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        
        # Check if restaurants are already seeded
        if Restaurant.query.first() is None:
            restaurants = [
                Restaurant(name='一蘭拉麵 台中朝富店', category='日式', price_level=2, distance=800, address='台中市西屯區朝富路2號', rating=4.5),
                Restaurant(name='屋馬燒肉 中港店', category='日式', price_level=3, distance=1500, address='台中市西屯區台灣大道三段300號', rating=4.8),
                Restaurant(name='輕井澤鍋物 公益店', category='火鍋', price_level=2, distance=2500, address='台中市西區公益路276號', rating=4.4),
                Restaurant(name='宮原眼科', category='甜點', price_level=2, distance=4000, address='台中市中區中山路20號', rating=4.3),
                Restaurant(name='麥當勞 台中逢甲店', category='速食', price_level=1, distance=500, address='台中市西屯區福星路427號', rating=4.0),
                Restaurant(name='星巴克 國家歌劇院門市', category='咖啡廳', price_level=2, distance=1200, address='台中市西屯區惠來路二段101號', rating=4.6),
                Restaurant(name='春水堂 創始店', category='台式', price_level=2, distance=3500, address='台中市西區四維街30號', rating=4.2),
                Restaurant(name='俺達の肉屋', category='日式', price_level=4, distance=2000, address='台中市西區公益路192-1號', rating=4.9),
                Restaurant(name='茶六燒肉堂 朝富店', category='日式', price_level=3, distance=900, address='台中市西屯區朝富路258號', rating=4.7),
                Restaurant(name='刁民酸菜魚 逢甲店', category='台式', price_level=2, distance=600, address='台中市西屯區福星路591號', rating=4.5),
                Restaurant(name='鼎泰豐 台中店', category='台式', price_level=3, distance=1800, address='台中市西屯區台灣大道三段251號B2', rating=4.7),
                Restaurant(name='激旨燒鳥 逢甲總店', category='日式', price_level=2, distance=450, address='台中市西屯區文華路150-18號', rating=4.3),
                Restaurant(name='太初麵食', category='台式', price_level=2, distance=2800, address='台中市南屯區公益路二段115號', rating=4.2),
                Restaurant(name='逢甲溫家地瓜球', category='甜點', price_level=1, distance=300, address='台中市西屯區文華路99-2號', rating=4.1),
                Restaurant(name='炭火燒肉工房', category='日式', price_level=2, distance=1600, address='台中市西區美村路一段112號', rating=4.4),
                # 從 D1443860 補回來的逢甲美食
                Restaurant(name='日船章魚小丸子 總店', category='小吃', price_level=1, distance=400, address='台中市西屯區文華路15號', rating=4.2),
                Restaurant(name='逢甲冰火菠蘿油', category='甜點', price_level=1, distance=350, address='台中市西屯區逢甲路20號', rating=4.3),
                Restaurant(name='大甲芋頭城 逢甲店', category='甜點', price_level=1, distance=320, address='台中市西屯區福星路461巷', rating=4.4),
                Restaurant(name='尊品原汁牛肉麵', category='麵食', price_level=1, distance=650, address='台中市西屯區福星路300號', rating=4.1),
                Restaurant(name='赤鬼炙燒牛排 逢甲店', category='西式', price_level=2, distance=550, address='台中市西屯區文華路11號', rating=4.2),
                Restaurant(name='炳叔烤玉米 逢甲店', category='小吃', price_level=1, distance=450, address='台中市西屯區福星路476號', rating=4.5),
                Restaurant(name='官芝霖大腸包小腸', category='小吃', price_level=1, distance=200, address='台中市西屯區逢甲路22號', rating=4.0),
                Restaurant(name='一心素食臭豆腐', category='素食', price_level=1, distance=400, address='台中市西屯區福星路461巷2號', rating=4.4),
            ]
            db.session.bulk_save_objects(restaurants)
            db.session.commit()
            print("Successfully seeded the database with restaurants!")

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, host='127.0.0.1', port=5000)
