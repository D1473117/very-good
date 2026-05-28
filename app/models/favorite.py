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

def create_favorite(user_id, restaurant_id):
    """
    新增一筆最愛收藏記錄。
    
    :param user_id: 用戶 ID
    :param restaurant_id: 餐廳 ID
    :return: 新增成功的收藏 ID，若失敗或重複則回傳 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Favorite (user_id, restaurant_id) VALUES (?, ?)', (user_id, restaurant_id))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Already favorited
    except Exception as e:
        print(f"Error creating favorite: {e}")
        return None

def get_all_favorites():
    """
    取得所有最愛收藏記錄。
    
    :return: 收藏字典列表
    """
    try:
        conn = get_db_connection()
        favorites = conn.execute('SELECT * FROM Favorite').fetchall()
        conn.close()
        return [dict(f) for f in favorites]
    except Exception as e:
        print(f"Error getting all favorites: {e}")
        return []

def get_favorite_by_id(favorite_id):
    """
    根據 ID 取得單筆最愛收藏記錄。
    
    :param favorite_id: 收藏主鍵 ID
    :return: 收藏字典，若不存在則回傳 None
    """
    try:
        conn = get_db_connection()
        fav = conn.execute('SELECT * FROM Favorite WHERE id = ?', (favorite_id,)).fetchone()
        conn.close()
        return dict(fav) if fav else None
    except Exception as e:
        print(f"Error getting favorite by id {favorite_id}: {e}")
        return None

def delete_favorite(favorite_id):
    """
    根據 ID 刪除最愛收藏記錄。
    
    :param favorite_id: 收藏主鍵 ID
    :return: 刪除是否成功 (True/False)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Favorite WHERE id = ?', (favorite_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error deleting favorite {favorite_id}: {e}")
        return False

