from app import create_app, db
from app.models.restaurant import Restaurant

app = create_app()

new_restaurants = [
    Restaurant(name='日船章魚小丸子 總店', category='小吃', price_level=1, distance=400, address='台中市西屯區文華路15號', rating=4.2),
    Restaurant(name='逢甲冰火菠蘿油', category='甜點', price_level=1, distance=350, address='台中市西屯區逢甲路20號', rating=4.3),
    Restaurant(name='大甲芋頭城 逢甲店', category='甜點', price_level=1, distance=320, address='台中市西屯區福星路461巷', rating=4.4),
    Restaurant(name='尊品原汁牛肉麵', category='麵食', price_level=1, distance=650, address='台中市西屯區福星路300號', rating=4.1),
    Restaurant(name='赤鬼炙燒牛排 逢甲店', category='西式', price_level=2, distance=550, address='台中市西屯區文華路11號', rating=4.2),
    Restaurant(name='炳叔烤玉米 逢甲店', category='小吃', price_level=1, distance=450, address='台中市西屯區福星路476號', rating=4.5),
    Restaurant(name='官芝霖大腸包小腸', category='小吃', price_level=1, distance=200, address='台中市西屯區逢甲路22號', rating=4.0),
    Restaurant(name='一心素食臭豆腐', category='素食', price_level=1, distance=400, address='台中市西屯區福星路461巷2號', rating=4.4),
]

with app.app_context():
    for r in new_restaurants:
        if Restaurant.query.filter_by(name=r.name).first() is None:
            db.session.add(r)
    db.session.commit()
    print("Missing Fengchia restaurants added successfully!")
