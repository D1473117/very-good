import random
import sqlite3
from app.models.base import get_db_connection

def toggle_favorite(user_id, restaurant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if already favorited
    fav = cursor.execute('SELECT * FROM Favorite WHERE user_id = ? AND restaurant_id = ?', 
                         (user_id, restaurant_id)).fetchone()
    
    is_fav = False
    if fav:
        cursor.execute('DELETE FROM Favorite WHERE user_id = ? AND restaurant_id = ?', 
                       (user_id, restaurant_id))
    else:
        cursor.execute('INSERT INTO Favorite (user_id, restaurant_id) VALUES (?, ?)', 
                       (user_id, restaurant_id))
        is_fav = True
        
    conn.commit()
    conn.close()
    return is_fav

def is_user_favorited(user_id, restaurant_id):
    if not user_id:
        return False
    conn = get_db_connection()
    fav = conn.execute('SELECT 1 FROM Favorite WHERE user_id = ? AND restaurant_id = ?', 
                       (user_id, restaurant_id)).fetchone()
    conn.close()
    return fav is not None

def get_user_favorites(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Join with Restaurant to get restaurant details
    favorites = cursor.execute('''
        SELECT r.* FROM Restaurant r
        JOIN Favorite f ON r.id = f.restaurant_id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(f) for f in favorites]

def get_random_favorite(user_id):
    favorites = get_user_favorites(user_id)
    if favorites:
        selected = random.choice(favorites)
        selected['is_favorited'] = True  # It is definitely favorited since it is drawn from favorites
        return selected
    return None
