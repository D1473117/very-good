from app.models.database import get_db_connection

def add_history(session_id, restaurant_id, restaurant_name, lat, lng):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO recommendation_history (session_id, restaurant_id, restaurant_name, lat, lng) VALUES (?, ?, ?, ?, ?)',
            (session_id, restaurant_id, restaurant_name, lat, lng)
        )
        conn.commit()
    except Exception as e:
        print(f"Error adding history: {e}")
    finally:
        conn.close()

def get_history(session_id):
    conn = get_db_connection()
    rows = conn.execute(
        '''SELECT rh.*, r.category, r.budget_level, r.google_maps_url 
           FROM recommendation_history rh
           LEFT JOIN restaurants r ON rh.restaurant_id = r.id
           WHERE rh.session_id = ? 
           ORDER BY rh.created_at DESC''',
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_history_feedback(session_id, history_id, user_rating, comment):
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE recommendation_history SET user_rating = ?, comment = ? WHERE id = ? AND session_id = ?',
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
