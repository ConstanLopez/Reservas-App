from app.database import fetch_query

class Participante:
    @staticmethod
    def get_by_email(email):
        """Obtiene participante por email"""
        query = """
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT ppa.rol) as roles,
                   GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            WHERE p.email = %s
            GROUP BY p.ci
        """
        rows = fetch_query(query, (email,))
        if rows:
            participante = rows[0]
            # Convertir roles y programas en listas
            participante['roles'] = participante['roles'].split(',') if participante['roles'] else []
            participante['programas'] = participante['programas'].split(',') if participante['programas'] else []
            return participante
        return None
    
    @staticmethod
    def get_by_ci(ci):
        """Obtiene participante por CI"""
        query = """
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT ppa.rol) as roles,
                   GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            WHERE p.ci = %s
            GROUP BY p.ci
        """
        rows = fetch_query(query, (ci,))
        if rows:
            participante = rows[0]
            participante['roles'] = participante['roles'].split(',') if participante['roles'] else []
            participante['programas'] = participante['programas'].split(',') if participante['programas'] else []
            return participante
        return None
    
    @staticmethod
    def tiene_sancion_activa(ci):
        """Verifica si el participante tiene una sanción activa"""
        query = """
            SELECT * FROM sancion_partcipante
            WHERE ci_participante = %s 
            AND CURDATE() BETWEEN fecha_inicio AND fecha_fin
        """
        rows = fetch_query(query, (ci,))
        return len(rows) > 0
    
    @staticmethod
    def get_sancion_activa(ci):
        """Obtiene la sanción activa del participante"""
        query = """
            SELECT * FROM sancion_partcipante
            WHERE ci_participante = %s 
            AND CURDATE() BETWEEN fecha_inicio AND fecha_fin
            ORDER BY fecha_fin DESC
            LIMIT 1
        """
        rows = fetch_query(query, (ci,))
        return rows[0] if rows else None
    
    @staticmethod
    def es_docente(ci):
        """Verifica si el participante es docente"""
        query = """
            SELECT COUNT(*) as count FROM participante_programa_academico
            WHERE ci_participante = %s AND rol = 'docente'
        """
        rows = fetch_query(query, (ci,))
        return rows[0]['count'] > 0 if rows else False
    
    @staticmethod
    def es_posgrado(ci):
        """Verifica si el participante es de posgrado"""
        query = """
            SELECT COUNT(*) as count 
            FROM participante_programa_academico ppa
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            WHERE ppa.ci_participante = %s AND pa.tipo = 'posgrado'
        """
        rows = fetch_query(query, (ci,))
        return rows[0]['count'] > 0 if rows else False