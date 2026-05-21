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
