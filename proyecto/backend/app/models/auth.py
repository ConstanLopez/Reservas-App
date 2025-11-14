from app.database import execute_query, fetch_query

#execute_query(query, params) ejecuta una consulta NSERT, UPDATE o DELETE y devuelve True o False

#fetch query(query, params) ejecuta una consulta SELECT y devuelve los resultados como lista de diccionarios.

#Esta clase se encarga de los métodos de autenticación y gestión de los usuarios
class Auth:

    '''Los static method de python son métodos de la clase en si, no pertenecen a ninguna instancia'''
    @staticmethod
    
    def email_existe(email):
        """Verifica si el email ya está registrado en la base de datos"""
        query = "SELECT correo FROM login WHERE correo = %s"
        result = fetch_query(query, (email,))
        return len(result) > 0
    
    @staticmethod
    def ci_existe(ci):
        """Verifica si la CI ya existe en la base de datos"""
        query = "SELECT ci FROM participante WHERE ci = %s"
        result = fetch_query(query, (ci,))
        return len(result) > 0
    
    @staticmethod
    def crear_login(email, password_hash):
        """Crea registro en tabla login en la base de datos"""
        query = "INSERT INTO login (correo, contrasena) VALUES (%s, %s)"
        print("ejecutando query")
        result = execute_query(query, (email, password_hash))
        print(f"✅ Resultado execute_query: {result}")
        return result

    
    @staticmethod
    def crear_participante(ci, nombre, apellido, email):
        """Crea registro en tabla participante en la base de datos"""
        query = """
            INSERT INTO participante (ci, nombre, apellido, email)
            VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (ci, nombre, apellido, email))
    
   
    @staticmethod
    def asignar_programa(ci, nombre_programa, rol):
        """Asigna programa académico al participante en la base de datos"""
        query = """
            INSERT INTO participante_programa_academico 
            (ci_participante, nombre_programa, rol)
            VALUES (%s, %s, %s)
        """
        return execute_query(query, (ci, nombre_programa, rol))
    
    @staticmethod
    def obtener_usuario_por_email(email):
        """Obtiene datos completos del usuario por email desde la base de datos"""
        query = """
            SELECT 
                l.correo,
                l.contrasena as password_hash,
                p.ci,
                p.nombre,
                p.apellido,
                p.email
            FROM login l
            INNER JOIN participante p ON l.correo = p.email
            WHERE l.correo = %s
        """
        result = fetch_query(query, (email,))
        return result[0] if result else None
    
    @staticmethod
    def obtener_roles_usuario(ci):
        """Obtiene los roles y programas del usuario desde la base de datos"""
        query = """
            SELECT 
                ppa.rol,
                ppa.nombre_programa,
                pa.tipo
            FROM participante_programa_academico ppa
            INNER JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            WHERE ppa.ci_participante = %s
        """
        return fetch_query(query, (ci,))