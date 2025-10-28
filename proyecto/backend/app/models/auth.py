from app.database import execute_query, fetch_query

class Auth:
    
    @staticmethod
    def email_existe(email):
        """Verifica si el email ya está registrado"""
        query = "SELECT correo FROM login WHERE correo = %s"
        result = fetch_query(query, (email,))
        return len(result) > 0
    
    @staticmethod
    def ci_existe(ci):
        """Verifica si la CI ya existe"""
        query = "SELECT ci FROM participante WHERE ci = %s"
        result = fetch_query(query, (ci,))
        return len(result) > 0
    
    @staticmethod
    def crear_login(email, password_hash):
        """Crea registro en tabla login"""
        query = "INSERT INTO login (correo, contraseña) VALUES (%s, %s)"
        return execute_query(query, (email, password_hash))
    
    @staticmethod
    def crear_participante(ci, nombre, apellido, email):
        """Crea registro en tabla participante"""
        query = """
            INSERT INTO participante (ci, nombre, apellido, email)
            VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (ci, nombre, apellido, email))
    
    @staticmethod
    def asignar_programa(ci, nombre_programa, rol):
        """Asigna programa académico al participante"""
        query = """
            INSERT INTO participante_programa_academico 
            (ci_participante, nombre_programa, rol)
            VALUES (%s, %s, %s)
        """
        return execute_query(query, (ci, nombre_programa, rol))
    
    @staticmethod
    def obtener_usuario_por_email(email):
        """Obtiene datos completos del usuario por email"""
        query = """
            SELECT 
                l.correo,
                l.contraseña as password_hash,
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
        """Obtiene los roles y programas del usuario"""
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