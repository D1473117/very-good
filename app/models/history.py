from app.models.database import get_db_connection

# ==========================================================================
# 1. 實作技能要求：標準 CRUD 函式 (Dictionary-based)
# ==========================================================================

def create(data):
    """
    新增一筆推薦歷史紀錄。
    
    Args:
        data (dict): 包含歷史紀錄欄位的字典，欄位：session_id, restaurant_id, restaurant_name, lat, lng, user_rating, comment
        
    Returns:
        int: 新增成功後產生的歷史 ID，若失敗回傳 None。
    """
    conn = get_db_connection()
    new_id = None
    try:
        cursor = conn.execute(
            '''INSERT INTO recommendation_history 
               (session_id, restaurant_id, restaurant_name, place_id, lat, lng, user_rating, comment) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data.get('session_id'),
                data.get('restaurant_id'),
                data.get('restaurant_name'),
                data.get('place_id'),
                data.get('lat'),
                data.get('lng'),
                data.get('user_rating'),
                data.get('comment')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        print(f"Error creating recommendation history: {e}")
    finally:
        conn.close()
    return new_id

def get_all(session_id=None):
    """
    取得所有歷史紀錄。
    若帶入 session_id，則回傳該用戶的所有歷史紀錄。
    """
    conn = get_db_connection()
    try:
        if session_id:
            rows = conn.execute(
                'SELECT * FROM recommendation_history WHERE session_id = ? ORDER BY created_at DESC',
                (session_id,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT * FROM recommendation_history ORDER BY created_at DESC').fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting all history records: {e}")
        return []
    finally:
        conn.close()

def get_by_id(history_id):
    """
    取得單筆歷史紀錄。
    """
    conn = get_db_connection()
    try:
        row = conn.execute('SELECT * FROM recommendation_history WHERE id = ?', (history_id,)).fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error getting history record by id: {e}")
        return None
    finally:
        conn.close()

def update(history_id, data):
    """
    更新歷史紀錄。
    """
    conn = get_db_connection()
    try:
        conn.execute(
            '''UPDATE recommendation_history 
               SET session_id = ?, restaurant_id = ?, restaurant_name = ?, place_id = ?, lat = ?, lng = ?, user_rating = ?, comment = ?
               WHERE id = ?''',
            (
                data.get('session_id'),
                data.get('restaurant_id'),
                data.get('restaurant_name'),
                data.get('place_id'),
                data.get('lat'),
                data.get('lng'),
                data.get('user_rating'),
                data.get('comment'),
                history_id
            )
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating history record: {e}")
        return False
    finally:
        conn.close()

def delete(history_id):
    """
    刪除歷史紀錄。
    """
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM recommendation_history WHERE id = ?', (history_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting history record: {e}")
        return False
    finally:
        conn.close()


# ==========================================================================
# 2. 專案特有：歷史紀錄與心得評論邏輯
# ==========================================================================

def add_history(session_id, restaurant_id, restaurant_name, lat, lng):
    """
    相容方法：記錄一次成功的推薦結果。
    """
    return create({
        'session_id': session_id,
        'restaurant_id': restaurant_id,
        'restaurant_name': restaurant_name,
        'lat': lat,
        'lng': lng
    })

def get_history(session_id):
    """
    相容方法：獲取當前 Session 用戶的所有美食推薦歷史紀錄（按時間由新到舊排序），並 left join 餐廳資訊。
    """
    conn = get_db_connection()
    rows = conn.execute(
        '''SELECT rh.*, 
                  COALESCE(r.category, '小吃') as category, 
                  COALESCE(r.budget_level, 1) as budget_level, 
                  COALESCE(r.google_maps_url, 'https://maps.google.com/?q=' || rh.restaurant_name) as google_maps_url
           FROM recommendation_history rh
           LEFT JOIN restaurants r ON rh.restaurant_id = r.id
           WHERE rh.session_id = ? 
           ORDER BY rh.created_at DESC''',
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_history_feedback(session_id, history_id, user_rating, comment):
    """
    相容方法：更新指定推薦紀錄的星級評分與真實心得短評。
    """
    conn = get_db_connection()
    try:
        conn.execute(
            '''UPDATE recommendation_history 
               SET user_rating = ?, comment = ? 
               WHERE id = ? AND session_id = ?''',
            (user_rating, comment, history_id, session_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating history feedback: {e}")
        return False
    finally:
        conn.close()

def delete_history(session_id, history_id):
    """
    相容方法：刪除特定單筆歷史推薦紀錄。
    """
    conn = get_db_connection()
    try:
        conn.execute(
            'DELETE FROM recommendation_history WHERE id = ? AND session_id = ?',
            (history_id, session_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting history: {e}")
        return False
    finally:
        conn.close()
