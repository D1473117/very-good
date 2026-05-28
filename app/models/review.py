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

def get_all_reviews():
    """
    取得所有評價記錄。
    
    :return: 評價字典列表
    """
    try:
        conn = get_db_connection()
        reviews = conn.execute('SELECT * FROM Review').fetchall()
        conn.close()
        return [dict(r) for r in reviews]
    except Exception as e:
        print(f"Error getting all reviews: {e}")
        return []

def get_review_by_id(review_id):
    """
    根據 ID 取得單筆評價記錄。
    
    :param review_id: 評價主鍵 ID
    :return: 評價字典，若不存在則回傳 None
    """
    try:
        conn = get_db_connection()
        review = conn.execute('SELECT * FROM Review WHERE id = ?', (review_id,)).fetchone()
        conn.close()
        return dict(review) if review else None
    except Exception as e:
        print(f"Error getting review by id {review_id}: {e}")
        return None

def update_review(review_id, data):
    """
    更新指定 ID 的評價記錄。
    
    :param review_id: 評價主鍵 ID
    :param data: 包含欲更新欄位 (rating 或 comment) 的字典
    :return: 更新是否成功 (True/False)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        fields = []
        params = []
        
        if 'rating' in data:
            fields.append("rating = ?")
            params.append(int(data['rating']))
            
        if 'comment' in data:
            fields.append("comment = ?")
            params.append(data['comment'])
            
        if not fields:
            conn.close()
            return False
            
        params.append(review_id)
        query = f"UPDATE Review SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, params)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error updating review {review_id}: {e}")
        return False

