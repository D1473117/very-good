from app.models.database import get_db_connection

def add_favorite(session_id, restaurant_id):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT OR IGNORE INTO favorites (session_id, restaurant_id) VALUES (?, ?)',
            (session_id, restaurant_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding favorite: {e}")
        return False
    finally:
        conn.close()

def remove_favorite(session_id, restaurant_id):
    conn = get_db_connection()
    try:
        conn.execute(
            'DELETE FROM favorites WHERE session_id = ? AND restaurant_id = ?',
            (session_id, restaurant_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error removing favorite: {e}")
        return False
    finally:
        conn.close()

def is_favorite(session_id, restaurant_id):
    if not restaurant_id:
        return False
    conn = get_db_connection()
    row = conn.execute(
        'SELECT 1 FROM favorites WHERE session_id = ? AND restaurant_id = ?',
        (session_id, restaurant_id)
    ).fetchone()
    conn.close()
    return row is not None

def get_favorites(session_id):
    conn = get_db_connection()
    rows = conn.execute(
        '''SELECT r.* FROM restaurants r
           JOIN favorites f ON r.id = f.restaurant_id
           WHERE f.session_id = ?
           ORDER BY f.created_at DESC''',
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
