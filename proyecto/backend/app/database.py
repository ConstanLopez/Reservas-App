import mysql.connector
from mysql.connector import Error
from app.config import Config

#El parametro query es la cadena de texto que representa la instruccion SQL
#El parametro params=None representa un parametro opcional, reemplaza a los valores con %s de la consulta,
#  si no hay tales, se usa por defecto el valor  None
#3 metodos hacer conexion, fetchQuery, executeQuery
'''Esta funcion crea la conexión a las Base de Datos MySQL leyendo las credenciales de la clase config, que son tomadas del .env'''
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
        )
    #Excepcion por si detecta un error en la conexión, sino hay error, devuelve un objeto conexión activo (MySQL connection)
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

'''Esta función utiliza la conexión hecha en get_db_connection para poder ejecutar consultas de lectura'''
def fetch_query(query, params=None):
    conn = get_db_connection() #llamamos a la conexion hacia la db MySQL
    if not conn: 
        return []          # nunca None
    try:
        cur = conn.cursor(dictionary=True) #devuelve cada fila como un diccionario (más cómodo en Flask para enviar JSON).
        cur.execute(query, params or ()) #si params es None se usa  una tupla vacía
        rows = cur.fetchall()
        return rows or []  # lista vacía si no hay resultados
    except Error as e:
        print(f"Error ejecutando query: {e}")
        return [] # no devolvemos None, ya que no rompe endpoints, devolvemos un array vacio
    finally:
        try:
            cur.close(); conn.close() #cierra el cursor, liberando memoria y recursos. y la conexion con la db
        except: pass # previene un error, si alguna de las variables del bloque try del finally no existe


'''Esta  funcion sirve para modificar datos INSERT, UPDATE DELETE'''
def execute_query(query, params=None):
    conn = get_db_connection() #llamamos a la conexion hacia la db MySQL
    if not conn: # si no conecto
        print("No se conecto la base")
        return False 
    try:
        cur = conn.cursor() #creamos un cursor asociado a esa conexion
        cur.execute(query, params or ()) #ejecutamos la query con el cursor de esa conexion, esto previene inyeccion SQL ya que no concatena cadenas manulamente, y evalua si se pasaron o no parametros
        print("Se ejecuto la query")
        conn.commit() # guarda los cambios en la base de datos
        return True # si todo funciono bien devuelve True
    except Error as e:
        print(f"Error ejecutando query: {e}")
        conn.rollback() # revierte las transacciones, devuelve la bd al estado previo a la query
        return False # si algo sale mal devuelve False
    finally:
        try:
            cur.close(); conn.close() # cerramos el cursor y la conexión
        except: pass
