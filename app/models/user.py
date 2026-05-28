import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base import get_db_connection

def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO User (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Username already exists

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def check_user_credentials(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_all_users():
    """
    取得所有會員記錄。
    
    :return: 會員字典列表
    """
    try:
        conn = get_db_connection()
        users = conn.execute('SELECT id, username, created_at FROM User').fetchall()
        conn.close()
        return [dict(u) for u in users]
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []

def update_user(user_id, data):
    """
    更新指定 ID 的會員資訊 (例如密碼加密或變更名稱)。
    
    :param user_id: 會員 ID
    :param data: 包含欲更新欄位 (username 或密碼 password) 的字典
    :return: 更新是否成功 (True/False)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        fields = []
        params = []
        
        if 'username' in data:
            fields.append("username = ?")
            params.append(data['username'])
            
        if 'password' in data:
            fields.append("password_hash = ?")
            params.append(generate_password_hash(data['password']))
            
        if not fields:
            conn.close()
            return False
            
        params.append(user_id)
        query = f"UPDATE User SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, params)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error updating user {user_id}: {e}")
        return False

def delete_user(user_id):
    """
    刪除指定 ID 的會員記錄。
    
    :param user_id: 會員 ID
    :return: 刪除是否成功 (True/False)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM User WHERE id = ?', (user_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        return False

