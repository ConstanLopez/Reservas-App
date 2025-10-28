from app.database import execute_query, fetch_query

class Participante:
    
    @staticmethod
    def get_all():
        """Obtener todos los participantes"""
        query = "SELECT * FROM participante"
        return fetch_query(query)
    
    @staticmethod
    def get_by_ci(ci):
        """Obtener participante por CI"""
        query = "SELECT * FROM participante WHERE ci = %s"
        results = fetch_query(query, (ci,))
        return results[0] if results else None
    
    @staticmethod
    def create(data):
        """Crear nuevo participante"""
        query = """
            INSERT INTO participante (ci, nombre, apellido, email)
            VALUES (%s, %s, %s, %s)
        """
        params = (
            data['ci'],
            data['nombre'],
            data['apellido'],
            data['email']
        )
        return execute_query(query, params)
    
    @staticmethod
    def update(ci, data):
        """Actualizar participante"""
        query = """
            UPDATE participante 
            SET nombre = %s, apellido = %s, email = %s
            WHERE ci = %s
        """
        params = (
            data['nombre'],
            data['apellido'],
            data['email'],
            ci
        )
        return execute_query(query, params)
    
    @staticmethod
    def delete(ci):
        """Eliminar participante"""
        query = "DELETE FROM participante WHERE ci = %s"
        return execute_query(query, (ci,))