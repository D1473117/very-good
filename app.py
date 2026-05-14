from flask import Flask, render_template, request, jsonify
import sqlite3
import random
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql', mode='rb') as f:
        conn.cursor().executescript(f.read().decode('utf-8'))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    distance = data.get('distance', 3000)
    price_level = data.get('price_level', [1, 2, 3])
    cuisines = data.get('cuisines', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM restaurants WHERE distance <= ?"
    params = [distance]
    
    if cuisines:
        placeholders = ','.join(['?'] * len(cuisines))
        query += f" AND type IN ({placeholders})"
        params.extend(cuisines)
        
    cursor.execute(query, params)
    restaurants = cursor.fetchall()
    conn.close()
    
    # 根據價格篩選
    valid_restaurants = [r for r in restaurants if r['price_level'] in price_level]
    
    if not valid_restaurants:
        return jsonify({'error': '找不到符合條件的餐廳，請放寬篩選條件！'}), 404
        
    selected = random.choice(valid_restaurants)
    return jsonify(dict(selected))

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5000)
