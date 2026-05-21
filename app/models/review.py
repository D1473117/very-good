from app.models.base import get_db_connection

def add_review(user_id, restaurant_id, rating, comment):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Review (user_id, restaurant_id, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (user_id, restaurant_id, rating, comment))
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id

def get_restaurant_reviews(restaurant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    reviews = cursor.execute('''
        SELECT rv.*, u.username FROM Review rv
        JOIN User u ON rv.user_id = u.id
        WHERE rv.restaurant_id = ?
        ORDER BY rv.created_at DESC
    ''', (restaurant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in reviews]

def get_user_reviews(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    reviews = cursor.execute('''
        SELECT rv.*, r.name as restaurant_name, r.photo_url FROM Review rv
        JOIN Restaurant r ON rv.restaurant_id = r.id
        WHERE rv.user_id = ?
        ORDER BY rv.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in reviews]

def delete_review(review_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ensure the review belongs to the user
    cursor.execute('DELETE FROM Review WHERE id = ? AND user_id = ?', (review_id, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0
