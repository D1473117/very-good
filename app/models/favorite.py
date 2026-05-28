from app.models.database import get_db_connection

# ==========================================================================
# 1. 實作技能要求：標準 CRUD 函式 (Dictionary-based)
# ==========================================================================

def create(data):
    """
    新增一筆收藏記錄。
    
    Args:
        data (dict): 包含收藏欄位的字典，欄位：session_id, restaurant_id
        
    Returns:
        int: 新增成功後產生的收藏 ID，若失敗回傳 None。
    """
    conn = get_db_connection()
    new_id = None
    try:
        cursor = conn.execute(
            'INSERT OR IGNORE INTO favorites (session_id, restaurant_id) VALUES (?, ?)',
            (data.get('session_id'), data.get('restaurant_id'))
        )
        conn.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        print(f"Error creating favorite record: {e}")
    finally:
        conn.close()
    return new_id

def get_all(session_id=None):
    """
    取得所有收藏記錄。
    若帶入 session_id，則回傳該用戶的所有收藏記錄。
    """
    conn = get_db_connection()
    try:
        if session_id:
            rows = conn.execute('SELECT * FROM favorites WHERE session_id = ?', (session_id,)).fetchall()
        else:
            rows = conn.execute('SELECT * FROM favorites').fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting all favorite records: {e}")
        return []
    finally:
        conn.close()

def get_by_id(favorite_id):
    """
    取得單筆收藏記錄。
    """
    conn = get_db_connection()
    try:
        row = conn.execute('SELECT * FROM favorites WHERE id = ?', (favorite_id,)).fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error getting favorite record by id: {e}")
        return None
    finally:
        conn.close()

def update(favorite_id, data):
    """
    更新收藏記錄。
    """
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE favorites SET session_id = ?, restaurant_id = ? WHERE id = ?',
            (data.get('session_id'), data.get('restaurant_id'), favorite_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating favorite record: {e}")
        return False
    finally:
        conn.close()

def delete(favorite_id):
    """
    刪除收藏記錄（基於主鍵 id）。
    """
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM favorites WHERE id = ?', (favorite_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting favorite record: {e}")
        return False
    finally:
        conn.close()


# ==========================================================================
# 2. 專案特有：口袋名單業務邏輯
# ==========================================================================

def add_favorite(session_id, restaurant_id):
    """
    相容方法：將指定餐廳加入當前 Session 的口袋名單中。
    """
    return create({'session_id': session_id, 'restaurant_id': restaurant_id}) is not None

def remove_favorite(session_id, restaurant_id):
    """
    相容方法：將指定餐廳從當前 Session 的口袋名單中移除（基於聯合鍵）。
    """
    conn = get_db_connection()
    try:
        conn.execute(
            'DELETE FROM favorites WHERE session_id = ? AND restaurant_id = ?',
            (session_id, restaurant_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error removing favorite by session and restaurant: {e}")
        return False
    finally:
        conn.close()

def is_favorite(session_id, restaurant_id):
    """
    相容方法：檢查指定餐廳是否已被當前 Session 收藏。
    """
    conn = get_db_connection()
    row = conn.execute(
        'SELECT id FROM favorites WHERE session_id = ? AND restaurant_id = ?',
        (session_id, restaurant_id)
    ).fetchone()
    conn.close()
    return row is not None

def get_favorites(session_id):
    """
    相容方法：讀取當前 Session 用戶的所有收藏口袋名單詳情。
    """
    conn = get_db_connection()
    rows = conn.execute(
        '''SELECT r.* 
           FROM favorites f
           JOIN restaurants r ON f.restaurant_id = r.id
           WHERE f.session_id = ?
           ORDER BY f.created_at DESC''',
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
