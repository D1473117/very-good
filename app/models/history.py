from app.models.database import get_db_connection

def add_history(session_id, restaurant_name, lat, lng):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO recommendation_history (session_id, restaurant_name, lat, lng) VALUES (?, ?, ?, ?)',
            (session_id, restaurant_name, lat, lng)
        )
        conn.commit()
    except Exception as e:
        print(f"Error adding history: {e}")
    finally:
        conn.close()
