import mysql.connector
from mysql.connector import Error
from app.config import Config

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
        )
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def fetch_query(query, params=None):
    conn = get_db_connection()
    if not conn:
        return []          # nunca None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        rows = cur.fetchall()
        return rows or []  # lista vacía si no hay resultados
    except Error as e:
        print(f"Error ejecutando query: {e}")
        return []
    finally:
        try:
            cur.close(); conn.close()
        except: pass

def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        return True
    except Error as e:
        print(f"Error ejecutando query: {e}")
        conn.rollback()
        return False
    finally:
        try:
            cur.close(); conn.close()
        except: pass
